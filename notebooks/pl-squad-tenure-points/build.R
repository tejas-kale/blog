# Builds the club-season table from the saved retrieval.
# Human-review-critical functions are sourced from the tangled files.

.libPaths(c("/tmp/r-lib", .libPaths()))
args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
root <- if (length(file_arg)) {
  dirname(normalizePath(sub("^--file=", "", file_arg[[1]])))
} else {
  normalizePath("notebooks/pl-squad-tenure-points")
}
setwd(root)
source("regulars.R")
source("tenure.R")
source("points.R")
source("correlation.R")
source("resolution.R")
source("plotting.R")

read_table <- function(path) {
  utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
}

canon_or_keep <- function(name) {
  tryCatch(canonical_club(name), error = function(e) name)
}

normalize_person_name <- function(name) {
  name <- iconv(enc2utf8(name), to = "ASCII//TRANSLIT")
  name[is.na(name)] <- ""
  name <- tolower(name)
  name <- gsub("[^a-z ]", "", name)
  gsub("\\s+", " ", trimws(name))
}

message("Reading saved tables")
seasons <- 1996:2026
match_rows <- do.call(rbind, lapply(seasons, function(end_year) {
  path <- file.path("raw", "matches", paste0(end_year, ".csv"))
  if (!file.exists(path)) stop("Missing match file for ", end_year)
  matches <- read_table(path)
  if (!"FTR" %in% names(matches) && "Res" %in% names(matches)) matches$FTR <- matches$Res
  matches <- matches[matches$Div == "E0" & matches$FTR %in% c("H", "D", "A"), , drop = FALSE]
  if (nrow(matches) != 380) stop("Season ", end_year, " has ", nrow(matches), " matches")
  points <- results_points_from_matches(matches)
  points$season_end <- end_year
  points$club <- vapply(points$club, canonical_club, character(1))
  points
}))

official <- read_table("raw/fbref-table.csv")
if (length(unique(official$season_end)) != 31) {
  stop("FBref tables cover ", length(unique(official$season_end)), " seasons")
}
official$club <- vapply(official$team, canonical_club, character(1))
official$points <- as.integer(official$points)

gaps <- merge(
  data.frame(club = official$club, season_end = official$season_end, official_points = official$points, stringsAsFactors = FALSE),
  data.frame(club = match_rows$club, season_end = match_rows$season_end, results_points = match_rows$points, matches = match_rows$matches, stringsAsFactors = FALSE),
  by = c("club", "season_end")
)
if (nrow(gaps) != nrow(official) || nrow(gaps) != nrow(match_rows)) {
  stop("Club-season mismatch between the match file and the FBref table")
}
gaps$gap <- gaps$official_points - gaps$results_points
unexplained <- unexplained_points_gaps(gaps, named_deductions())
dir.create("out", showWarnings = FALSE)
utils::write.csv(gaps, "out/points-reconciliation.csv", row.names = FALSE)
if (nrow(unexplained) > 0) {
  utils::write.csv(unexplained, "out/unexplained-points-gaps.csv", row.names = FALSE)
  stop("Unexplained points gaps: ", nrow(unexplained))
}

players <- read_table("raw/fbref-players.csv")
players$club <- vapply(players$fbref_club, canonical_club, character(1))
players$starts <- as.integer(players$starts)
players$appearances <- as.integer(players$appearances)
players <- players[!duplicated(players[c("season_end", "club", "fbref_id")]), , drop = FALSE]

squads <- read_table("raw/tm-squads.csv")
squads$club <- vapply(squads$tm_club, canon_or_keep, character(1))
squads$name_key <- normalize_person_name(squads$player)

if (!file.exists("org-resolution.csv")) {
  utils::write.csv(
    data.frame(
      season_end = integer(), club = character(), source_name = character(),
      fbref_id = character(), tm_id = character(), resolution = character(),
      note = character(), stringsAsFactors = FALSE
    ),
    "org-resolution.csv",
    row.names = FALSE
  )
}
org <- read_table("org-resolution.csv")

match_regulars <- function(cut) {
  regulars <- regulars_for_cut(players, cut)
  regulars$name_key <- normalize_person_name(regulars$player)
  regulars$auto_status <- "unmatched"
  regulars$tm_id <- NA_character_
  regulars$source_name <- regulars$player
  for (i in seq_len(nrow(regulars))) {
    hit <- squads$season_end == regulars$season_end[[i]] &
      squads$club == regulars$club[[i]] &
      squads$name_key == regulars$name_key[[i]] &
      nzchar(regulars$name_key[[i]])
    ids <- unique(squads$tm_id[hit])
    if (length(ids) == 1) {
      regulars$auto_status[[i]] <- "unique"
      regulars$tm_id[[i]] <- ids
    } else if (length(ids) > 1) {
      regulars$auto_status[[i]] <- "ambiguous"
    }
  }
  apply_org_resolution(regulars, org)
}

message("Matching regulars to squad lists")
matched <- list(starts = match_regulars("starts"), appearances = match_regulars("appearances"))
flagged <- rbind(
  matched$starts[!matched$starts$enters, c("season_end", "club", "source_name", "fbref_id", "tm_id", "auto_status")],
  matched$appearances[!matched$appearances$enters, c("season_end", "club", "source_name", "fbref_id", "tm_id", "auto_status")]
)
flagged <- flagged[!duplicated(flagged), , drop = FALSE]
utils::write.csv(flagged, "out/ambiguous-players.csv", row.names = FALSE)

needed_ids <- unique(c(matched$starts$tm_id[matched$starts$enters], matched$appearances$tm_id[matched$appearances$enters]))
needed_ids <- needed_ids[!is.na(needed_ids)]
id_file <- "raw/transfer-ids.txt"
dir.create("raw", showWarnings = FALSE)
writeLines(needed_ids, id_file)
message("Transfer histories: ", length(needed_ids))
status <- system2("python3", c("retrieve.py", "--transfers", id_file))
if (status != 0) stop("Transfer history retrieval failed")

is_youth <- function(club) {
  grepl("youth|yth|\\bu1[6-9]\\b|\\bu2[1-3]\\b", club, ignore.case = TRUE, perl = TRUE)
}

message("Reading transfer histories")
dropped_dates <- list()
transfers <- do.call(rbind, lapply(needed_ids, function(player_id) {
  path <- file.path("raw", "transfers", paste0(player_id, ".json"))
  if (!file.exists(path) || file.info(path)$size < 20) stop("Missing transfer history ", player_id)
  payload <- jsonlite::fromJSON(path, simplifyVector = FALSE)
  rows <- payload$transfers
  if (length(rows) == 0) {
    return(data.frame(
      player_id = character(), date = character(), club_from = character(),
      club_to = character(), transfer_type = character(), stringsAsFactors = FALSE
    ))
  }
  parsed_rows <- lapply(rows, function(row) {
    fee <- tolower(if (is.null(row$fee)) "" else as.character(row$fee))
    from <- row$from$clubName
    to <- row$to$clubName
    date <- row$dateUnformatted
    parsed <- if (is.null(date) || !nzchar(date)) as.Date(NA) else tryCatch(as.Date(date), error = function(e) as.Date(NA))
    if (is.na(parsed)) {
      dropped_dates[[length(dropped_dates) + 1L]] <<- data.frame(
        player_id = player_id,
        date = if (is.null(date)) "" else as.character(date),
        club_from = if (is.null(from)) "" else as.character(from),
        club_to = if (is.null(to)) "" else as.character(to),
        stringsAsFactors = FALSE
      )
      return(NULL)
    }
    if (is.null(from) || is.null(to) || !nzchar(from) || !nzchar(to)) {
      stop("Missing transfer club for ", player_id)
    }
    type <- if (grepl("end of loan", fee)) {
      "end_loan"
    } else if (grepl("loan", fee)) {
      "loan"
    } else if (is_youth(from) && !is_youth(to)) {
      "senior"
    } else if (is_youth(from) || is_youth(to)) {
      "academy"
    } else {
      "permanent"
    }
    data.frame(
      player_id = player_id,
      date = date,
      club_from = canon_or_keep(from),
      club_to = canon_or_keep(to),
      transfer_type = type,
      stringsAsFactors = FALSE
    )
  })
  parsed_rows <- parsed_rows[!vapply(parsed_rows, is.null, logical(1))]
  if (length(parsed_rows) == 0) {
    return(data.frame(
      player_id = character(), date = character(), club_from = character(),
      club_to = character(), transfer_type = character(), stringsAsFactors = FALSE
    ))
  }
  do.call(rbind, parsed_rows)
}))
utils::write.csv(
  if (length(dropped_dates) == 0) {
    data.frame(player_id = character(), date = character(), club_from = character(), club_to = character(), stringsAsFactors = FALSE)
  } else {
    do.call(rbind, dropped_dates)
  },
  "out/unparsed-transfer-dates.csv",
  row.names = FALSE
)
message("Computing tenure")
spells <- involvement_from_transfers(transfers, through_season_end = 2026L)
tenured <- senior_squad_tenure(spells)
tenured <- tenured[!is.na(tenured$tenure), c("player_id", "season_end", "club", "tenure")]

attach_tenure <- function(regulars) {
  regulars$tenure <- NA_real_
  for (i in which(regulars$enters)) {
    hit <- tenured$player_id == regulars$tm_id[[i]] &
      tenured$season_end == regulars$season_end[[i]] &
      tenured$club == regulars$club[[i]]
    if (sum(hit) == 1) regulars$tenure[[i]] <- tenured$tenure[[which(hit)]]
  }
  regulars$tenure_missing <- regulars$enters & is.na(regulars$tenure)
  regulars
}

summarise_cut <- function(cut, regulars) {
  regulars <- attach_tenure(regulars)
  blocked <- club_seasons_blocked_by_unresolved(regulars)
  missing <- unique(regulars[regulars$tenure_missing, c("club", "season_end")])
  if (nrow(missing) > 0) {
    blocked <- unique(rbind(blocked, missing))
  }
  kept <- regulars[regulars$enters & !is.na(regulars$tenure), , drop = FALSE]
  blocked_key <- paste(blocked$club, blocked$season_end)
  kept <- kept[!paste(kept$club, kept$season_end) %in% blocked_key, , drop = FALSE]
  medians <- club_season_median_tenure(kept)
  points <- gaps[c("club", "season_end", "results_points")]
  club_seasons <- merge(medians, points, by = c("club", "season_end"))
  correlations <- within_club_correlations(club_seasons, min_seasons = 10L)
  summary <- lead_summary(correlations)
  boot <- bootstrap_median_correlation(club_seasons, n_replicates = 2000L, seed = 2026L, min_seasons = 10L)
  utils::write.csv(club_seasons, file.path("out", paste0("club-seasons-", cut, ".csv")), row.names = FALSE)
  utils::write.csv(correlations, file.path("out", paste0("correlations-", cut, ".csv")), row.names = FALSE)
  utils::write.csv(boot$club_intervals, file.path("out", paste0("club-intervals-", cut, ".csv")), row.names = FALSE)
  utils::write.csv(
    data.frame(
      replicate = seq_along(boot$replicate_medians),
      median_correlation = boot$replicate_medians,
      stringsAsFactors = FALSE
    ),
    file.path("out", paste0("bootstrap-", cut, ".csv")),
    row.names = FALSE
  )
  ranked <- correlations[correlations$defined, , drop = FALSE]
  ranked <- ranked[order(-ranked$n_seasons, ranked$club), , drop = FALSE]
  plotted <- utils::head(ranked, 10)
  for (i in seq_len(nrow(plotted))) {
    export_club_plot(
      file.path("out", paste0("club-seasons-", cut, ".csv")),
      plotted$club[[i]],
      file.path("out", "plots", cut, paste0(gsub("[^A-Za-z0-9]+", "-", plotted$club[[i]]), ".svg"))
    )
  }
  list(
    cut = cut,
    summary = summary,
    sentence = undefined_share_sentence(summary),
    interval = boot$interval,
    n_club_seasons = nrow(club_seasons),
    n_blocked = nrow(blocked),
    plotted = plotted$club,
    absent_clubs = sort(setdiff(unique(gaps$club), correlations$club))
  )
}

message("Summarising both cuts")
results <- list(
  starts = summarise_cut("starts", matched$starts),
  appearances = summarise_cut("appearances", matched$appearances)
)
jsonlite::write_json(results, "out/summary.json", auto_unbox = TRUE, pretty = TRUE, digits = 8)
message("Wrote out/summary.json")


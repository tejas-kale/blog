# A campaign is 1 September through 31 May. A player who is at one senior
# club for that whole stretch adds 1. A loan that covers that whole stretch
# is a full-season loan: the parent records 0 and the streak is wiped, and
# the loan club adds 1. Any other split of the stretch is a mid-season
# 0.5. A permanent move before 1 September gives the new club the season.
# A later return after a permanent move or a full-season loan starts at 1.

campaign_start <- function(season_end) {
  as.Date(sprintf("%d-09-01", season_end - 1L))
}

campaign_end <- function(season_end) {
  as.Date(sprintf("%d-05-31", season_end))
}

# June, July, and August belong to the season that is about to be played.
season_holding_move <- function(date) {
  date <- as.Date(date)
  year <- as.integer(format(date, "%Y"))
  month <- as.integer(format(date, "%m"))
  if (month >= 6L) year + 1L else year
}

involvement_from_transfers <- function(transfers, through_season_end) {
  transfers$date <- as.Date(transfers$date)
  transfers$player_id <- as.character(transfers$player_id)
  empty <- data.frame(
    player_id = character(),
    season_end = integer(),
    club = character(),
    involvement = character(),
    stringsAsFactors = FALSE
  )
  if (nrow(transfers) == 0) return(empty)

  pieces <- lapply(split(transfers, transfers$player_id), function(events) {
    events <- events[order(events$date, seq_len(nrow(events))), , drop = FALSE]
    changes <- data.frame(
      date = as.Date(character()),
      club = character(),
      kind = character(),
      parent = character(),
      stringsAsFactors = FALSE
    )
    club <- NA_character_
    kind <- NA_character_
    parent <- NA_character_
    for (i in seq_len(nrow(events))) {
      type <- events$transfer_type[[i]]
      from <- events$club_from[[i]]
      to <- events$club_to[[i]]
      if (type == "academy") {
        club <- to
        kind <- "academy"
        parent <- NA_character_
      } else if (type == "senior" || type == "permanent") {
        club <- to
        kind <- "senior"
        parent <- NA_character_
      } else if (type == "loan") {
        parent <- from
        club <- to
        kind <- "loan"
      } else if (type == "end_loan") {
        club <- to
        youth_dest <- grepl("youth|yth|\\bu1[6-9]\\b|\\bu2[1-3]\\b", to, ignore.case = TRUE, perl = TRUE)
        kind <- if (isTRUE(youth_dest)) "academy" else "senior"
        parent <- NA_character_
      } else {
        stop("Unknown transfer_type: ", type)
      }
      changes <- rbind(changes, data.frame(
        date = events$date[[i]],
        club = club,
        kind = kind,
        parent = if (is.na(parent)) "" else parent,
        stringsAsFactors = FALSE
      ))
    }

    first_date <- min(events$date)
    first_season <- season_holding_move(first_date)
    rows <- empty
    for (season_end in seq.int(first_season, through_season_end)) {
      days <- seq(campaign_start(season_end), campaign_end(season_end), by = "day")
      idx <- findInterval(as.numeric(days), as.numeric(changes$date))
      active <- changes[idx[idx > 0], , drop = FALSE]
      if (nrow(active) == 0) next
      senior_or_loan <- active[active$kind %in% c("senior", "loan"), , drop = FALSE]
      if (nrow(senior_or_loan) == 0) {
        academy <- active[active$kind == "academy", , drop = FALSE]
        if (nrow(academy) > 0) {
          rows <- rbind(rows, data.frame(
            player_id = events$player_id[[1]],
            season_end = season_end,
            club = academy$club[[1]],
            involvement = "academy",
            stringsAsFactors = FALSE
          ))
        }
        next
      }

      clubs <- unique(senior_or_loan$club)
      loan_clubs <- unique(senior_or_loan$club[senior_or_loan$kind == "loan"])
      senior_clubs <- unique(senior_or_loan$club[senior_or_loan$kind == "senior"])
      parents <- unique(senior_or_loan$parent[senior_or_loan$kind == "loan" & senior_or_loan$parent != ""])

      add <- function(club_name, involvement) {
        data.frame(
          player_id = events$player_id[[1]],
          season_end = season_end,
          club = club_name,
          involvement = involvement,
          stringsAsFactors = FALSE
        )
      }

      if (length(clubs) == 1 && length(loan_clubs) == 1 && length(senior_clubs) == 0) {
        rows <- rbind(
          rows,
          add(parents[[1]], "full_loan_out"),
          add(loan_clubs[[1]], "full_loan_in")
        )
      } else if (length(loan_clubs) == 0 && length(senior_clubs) == 1) {
        rows <- rbind(rows, add(senior_clubs[[1]], "senior"))
      } else if (length(loan_clubs) >= 1 && length(intersect(parents, senior_clubs)) >= 1) {
        parent <- intersect(parents, senior_clubs)[[1]]
        rows <- rbind(rows, add(parent, "mid_loan_parent"))
        for (loan_club in loan_clubs) {
          rows <- rbind(rows, add(loan_club, "mid_loan_in"))
        }
      } else if (length(loan_clubs) == 0 && length(senior_clubs) >= 2) {
        start_idx <- idx[idx > 0][[1]]
        end_idx <- idx[idx > 0][[length(idx[idx > 0])]]
        start_club <- changes$club[[start_idx]]
        rows <- rbind(rows, add(start_club, "mid_move_out"))
        for (other in setdiff(senior_clubs, start_club)) {
          rows <- rbind(rows, add(other, "mid_move_in"))
        }
      } else if (length(loan_clubs) >= 1 && length(senior_clubs) == 0) {
        parent <- parents[[1]]
        rows <- rbind(rows, add(parent, "full_loan_out"))
        for (loan_club in loan_clubs) {
          rows <- rbind(rows, add(loan_club, "full_loan_in"))
        }
      } else if (length(clubs) == 1) {
        # The same club occupies every campaign day, partly on loan and partly as senior.
        rows <- rbind(rows, add(clubs[[1]], "senior"))
        for (parent in setdiff(parents, clubs[[1]])) {
          rows <- rbind(rows, add(parent, "full_loan_out"))
        }
      } else {
        # Any other split of the campaign is 0.5 at each club in the stretch.
        start_idx <- idx[idx > 0][[1]]
        start_club <- changes$club[[start_idx]]
        if (start_club %in% senior_clubs) {
          rows <- rbind(rows, add(start_club, "mid_move_out"))
        } else if (start_club %in% loan_clubs) {
          rows <- rbind(rows, add(start_club, "mid_loan_in"))
        }
        for (loan_club in setdiff(loan_clubs, start_club)) {
          rows <- rbind(rows, add(loan_club, "mid_loan_in"))
        }
        for (senior_club in setdiff(senior_clubs, start_club)) {
          rows <- rbind(rows, add(senior_club, "mid_move_in"))
        }
        for (parent in setdiff(parents, c(senior_clubs, loan_clubs))) {
          rows <- rbind(rows, add(parent, "mid_move_out"))
        }
      }
    }

    permanent <- events[events$transfer_type == "permanent", , drop = FALSE]
    for (i in seq_len(nrow(permanent))) {
      season_end <- season_holding_move(permanent$date[[i]])
      if (season_end > through_season_end) next
      left <- permanent$club_from[[i]]
      already <- rows$player_id == events$player_id[[1]] &
        rows$season_end == season_end &
        rows$club == left
      if (!any(already)) {
        rows <- rbind(rows, data.frame(
          player_id = events$player_id[[1]],
          season_end = season_end,
          club = left,
          involvement = "spell_end",
          stringsAsFactors = FALSE
        ))
      }
    }
    rows
  })
  out <- do.call(rbind, pieces)
  rownames(out) <- NULL
  out
}

senior_squad_tenure <- function(spells) {
  spells$tenure <- NA_real_
  if (nrow(spells) == 0) return(spells)
  spells$player_id <- as.character(spells$player_id)
  spells$row_id <- seq_len(nrow(spells))
  for (player in unique(spells$player_id)) {
    idx <- which(spells$player_id == player)
    order_idx <- idx[order(spells$season_end[idx], spells$row_id[idx])]
    state <- list()
    for (i in order_idx) {
      club <- spells$club[[i]]
      involvement <- spells$involvement[[i]]
      carried <- if (is.null(state[[club]])) 0 else state[[club]]
      if (involvement == "academy" || involvement == "spell_end") {
        spells$tenure[[i]] <- NA_real_
        if (involvement == "spell_end") state[[club]] <- 0
        next
      }
      if (involvement == "full_loan_out") {
        spells$tenure[[i]] <- 0
        state[[club]] <- 0
        next
      }
      if (involvement %in% c("senior", "full_loan_in")) {
        carried <- carried + 1
        spells$tenure[[i]] <- carried
        state[[club]] <- carried
        next
      }
      if (involvement %in% c("mid_loan_parent", "mid_loan_in", "mid_move_in", "mid_move_out")) {
        carried <- carried + 0.5
        spells$tenure[[i]] <- carried
        state[[club]] <- if (involvement == "mid_move_out") 0 else carried
        next
      }
      stop("Unknown involvement: ", involvement)
    }
  }
  spells$row_id <- NULL
  spells
}

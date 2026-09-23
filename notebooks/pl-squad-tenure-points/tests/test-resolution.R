# A club-season with an unresolved regular stays out. An org-table match lets it in.
local({
  here <- "notebooks/pl-squad-tenure-points"
  if (!file.exists(file.path(here, "resolution.R"))) here <- "."
  source(file.path(here, "resolution.R"))

  regulars <- data.frame(
    season_end = c(2020L, 2020L),
    club = c("Alpha", "Alpha"),
    source_name = c("Known Player", "Mystery Player"),
    fbref_id = c("aaa", "bbb"),
    tm_id = c("1", NA),
    auto_status = c("unique", "unmatched"),
    stringsAsFactors = FALSE
  )
  org <- data.frame(
    season_end = integer(),
    club = character(),
    source_name = character(),
    fbref_id = character(),
    tm_id = character(),
    resolution = character(),
    note = character(),
    stringsAsFactors = FALSE
  )
  blocked <- club_seasons_blocked_by_unresolved(apply_org_resolution(regulars, org))
  stopifnot(nrow(blocked) == 1)
  stopifnot(blocked$club == "Alpha" && blocked$season_end == 2020L)

  org <- data.frame(
    season_end = 2020L,
    club = "Alpha",
    source_name = "Mystery Player",
    fbref_id = "bbb",
    tm_id = "99",
    resolution = "match",
    note = "same person",
    stringsAsFactors = FALSE
  )
  cleared <- club_seasons_blocked_by_unresolved(apply_org_resolution(regulars, org))
  stopifnot(nrow(cleared) == 0)
  cat("resolution ok\n")
})

# Seam: results points are 3 for a win and 1 for a draw.
# A gap is accepted only when it equals a named deduction.
local({
  here <- "notebooks/pl-squad-tenure-points"
  if (!file.exists(file.path(here, "points.R"))) here <- "."
  source(file.path(here, "points.R"))

  matches <- data.frame(
    HomeTeam = c("Alpha", "Alpha", "Beta"),
    AwayTeam = c("Beta", "Gamma", "Gamma"),
    FTR = c("H", "D", "A"),
    stringsAsFactors = FALSE
  )
  got <- results_points_from_matches(matches)
  got <- got[order(got$club), ]
  # Alpha: win + draw = 4. Beta: loss + loss = 0. Gamma: draw + win = 4.
  stopifnot(identical(got$club, c("Alpha", "Beta", "Gamma")))
  stopifnot(identical(got$points, c(4L, 0L, 4L)))
  stopifnot(identical(got$matches, c(2L, 2L, 2L)))

  gaps <- data.frame(
    club = c("Middlesbrough", "Portsmouth", "Everton", "Nottingham Forest", "Arsenal", "Leeds"),
    season_end = c(1997L, 2010L, 2024L, 2024L, 2024L, 1997L),
    gap = c(-3L, -9L, -8L, -4L, 0L, -1L),
    stringsAsFactors = FALSE
  )
  unexplained <- unexplained_points_gaps(gaps, named_deductions())
  stopifnot(nrow(unexplained) == 1)
  stopifnot(unexplained$club == "Leeds")
  stopifnot(unexplained$season_end == 1997L)
  stopifnot(canonical_club("Manchester Utd") == "Manchester United")
  stopifnot(canonical_club("Nott'm Forest") == "Nottingham Forest")
  stopifnot(canonical_club("Wimbledon FC (- 2004)") == "Wimbledon")
  stopifnot(canonical_club("Arsenal FC") == "Arsenal")
  cat("points ok\n")
})

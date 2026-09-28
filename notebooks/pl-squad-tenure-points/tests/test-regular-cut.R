# Seam: a count of 19 is out, and 20 and 21 are in. The two cuts are separate.
local({
  here <- "notebooks/pl-squad-tenure-points"
  if (!file.exists(file.path(here, "regulars.R"))) {
    here <- "."
  }
  source(file.path(here, "regulars.R"))

  players <- data.frame(
    player = c("nineteen", "twenty", "twentyone"),
    starts = c(19, 20, 21),
    appearances = c(21, 19, 20),
    stringsAsFactors = FALSE
  )

  by_starts <- regulars_for_cut(players, "starts")
  by_appearances <- regulars_for_cut(players, "appearances")

  stopifnot(identical(by_starts$player, c("twenty", "twentyone")))
  stopifnot(identical(by_appearances$player, c("nineteen", "twentyone")))
  stopifnot(!any(by_starts$starts < 20))
  stopifnot(!any(by_appearances$appearances < 20))
  cat("regular cut ok\n")
})

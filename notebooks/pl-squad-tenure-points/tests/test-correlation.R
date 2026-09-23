# Seam: the second script recomputes the median, the trimmed mean, and one
# bootstrap percentile without calling the notebook correlation function.
local({
  here <- "notebooks/pl-squad-tenure-points"
  if (!file.exists(file.path(here, "correlation.R"))) here <- "."
  source(file.path(here, "correlation.R"))

  pos <- data.frame(
    club = "Pos",
    season_end = 2000 + 1:10,
    median_tenure = 1:10,
    results_points = 1:10,
    stringsAsFactors = FALSE
  )
  neg <- data.frame(
    club = "Neg",
    season_end = 2000 + 1:10,
    median_tenure = 1:10,
    results_points = 10:1,
    stringsAsFactors = FALSE
  )
  flat <- data.frame(
    club = "Flat",
    season_end = 2000 + 1:10,
    median_tenure = rep(3, 10),
    results_points = 1:10,
    stringsAsFactors = FALSE
  )
  short <- data.frame(
    club = "Short",
    season_end = 2000 + 1:9,
    median_tenure = 1:9,
    results_points = 1:9,
    stringsAsFactors = FALSE
  )
  club_seasons <- rbind(pos, neg, flat, short)
  correlations <- within_club_correlations(club_seasons, min_seasons = 10L)
  summary <- lead_summary(correlations)

  stopifnot(abs(summary$median - 0) < 1e-12)
  stopifnot(abs(summary$trimmed_mean - 0) < 1e-12)
  stopifnot(abs(summary$spearman - 0) < 1e-12)
  stopifnot(abs(summary$undefined_share - 1 / 3) < 1e-12)
  stopifnot(identical(summary$undefined_clubs, "Flat"))
  stopifnot(identical(summary$below_min_clubs, "Short"))
  sentence <- undefined_share_sentence(summary)
  stopifnot(!is.na(sentence))
  stopifnot(grepl("Flat", sentence) || grepl("left out", sentence))

  both <- rbind(pos, neg)
  quiet <- undefined_share_sentence(lead_summary(within_club_correlations(both, 10L)))
  stopifnot(is.na(quiet))

  one <- data.frame(
    club = "Only",
    season_end = 1:10,
    median_tenure = 1:10,
    results_points = c(2, 4, 4, 8, 10, 10, 14, 16, 18, 18),
    stringsAsFactors = FALSE
  )
  boot <- bootstrap_median_correlation(one, n_replicates = 2000L, seed = 2026L, min_seasons = 10L)
  stopifnot(abs(boot$replicate_medians[[1]] - 0.9893840002) < 1e-9)
  stopifnot(length(boot$replicate_medians) == 2000L)

  tmp <- tempdir()
  multi_path <- file.path(tmp, "correlation-fixture.csv")
  one_path <- file.path(tmp, "bootstrap-fixture.csv")
  write.csv(club_seasons, multi_path, row.names = FALSE)
  write.csv(one, one_path, row.names = FALSE)

  second <- file.path(here, "second-correlation.R")
  multi_out <- system2("Rscript", c(second, multi_path), stdout = TRUE, stderr = TRUE)
  one_out <- system2("Rscript", c(second, one_path), stdout = TRUE, stderr = TRUE)
  grab <- function(lines, key) {
    hit <- grep(paste0("^", key, "="), lines, value = TRUE)
    as.numeric(sub(".*=", "", hit[[1]]))
  }
  stopifnot(abs(grab(multi_out, "median") - 0) < 1e-12)
  stopifnot(abs(grab(multi_out, "trimmed_mean") - 0) < 1e-12)
  stopifnot(abs(grab(multi_out, "spearman") - 0) < 1e-12)
  stopifnot(abs(grab(one_out, "percentile_97_5") - boot$interval[[2]]) < 1e-12)
  cat("correlation ok\n")
})

# Independent recomputation of the lead numbers.
# This file does not source correlation.R and does not call its functions.
#
# Usage: Rscript second-correlation.R club-seasons.csv
# The CSV has club, season_end, median_tenure, results_points.

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Pass the club-season CSV.")
club_seasons <- read.csv(args[[1]], stringsAsFactors = FALSE)

min_seasons <- 10L
clubs <- sort(unique(club_seasons$club))
defined <- numeric()
spearmans <- numeric()
undefined_n <- 0L
at_least_10 <- 0L
for (club in clubs) {
  d <- club_seasons[club_seasons$club == club, , drop = FALSE]
  if (nrow(d) < min_seasons) next
  at_least_10 <- at_least_10 + 1L
  if (length(unique(d$median_tenure)) < 2) {
    undefined_n <- undefined_n + 1L
    next
  }
  r <- suppressWarnings(cor(d$median_tenure, d$results_points, method = "pearson"))
  if (!is.finite(r)) {
    undefined_n <- undefined_n + 1L
  } else {
    defined <- c(defined, r)
    s <- suppressWarnings(cor(d$median_tenure, d$results_points, method = "spearman"))
    if (is.finite(s)) spearmans <- c(spearmans, s)
  }
}

counts <- table(club_seasons$club)
boot_clubs <- sort(names(counts)[counts >= min_seasons])
set.seed(2026)
replicate_medians <- rep(NA_real_, 2000L)
for (i in seq_len(2000L)) {
  cors <- numeric()
  for (club in boot_clubs) {
    d <- club_seasons[club_seasons$club == club, , drop = FALSE]
    d <- d[order(d$season_end), , drop = FALSE]
    drawn <- d[sample.int(nrow(d), nrow(d), replace = TRUE), , drop = FALSE]
    if (length(unique(drawn$median_tenure)) < 2) next
    r <- suppressWarnings(cor(drawn$median_tenure, drawn$results_points, method = "pearson"))
    if (is.finite(r)) cors <- c(cors, r)
  }
  if (length(cors) > 0) replicate_medians[[i]] <- median(cors)
}
percentile_97_5 <- as.numeric(quantile(replicate_medians, 0.975, na.rm = TRUE, names = FALSE, type = 7))

cat(sprintf("median=%.10f\n", median(defined)))
cat(sprintf("trimmed_mean=%.10f\n", mean(defined, trim = 0.1)))
cat(sprintf("spearman=%.10f\n", median(spearmans)))
cat(sprintf("percentile_97_5=%.10f\n", percentile_97_5))
cat(sprintf("undefined_share=%.10f\n", if (at_least_10 == 0) NA else undefined_n / at_least_10))

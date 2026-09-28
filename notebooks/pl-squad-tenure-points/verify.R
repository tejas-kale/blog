# Verification contract. Exits non-zero when a check fails.
.libPaths(c("/tmp/r-lib", .libPaths()))
args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)
root <- if (length(file_arg)) {
  dirname(normalizePath(sub("^--file=", "", file_arg[[1]])))
} else {
  normalizePath("notebooks/pl-squad-tenure-points")
}
setwd(root)

tests <- c(
  "tests/test-regular-cut.R",
  "tests/test-tenure-sheet.R",
  "tests/test-points.R",
  "tests/test-resolution.R",
  "tests/test-correlation.R",
  "tests/test-export.R"
)
for (test in tests) {
  message(test)
  source(test, chdir = FALSE)
}

if (file.exists("out/club-seasons-starts.csv")) {
  source("correlation.R")
  grab <- function(lines, key) {
    hit <- grep(paste0("^", key, "="), lines, value = TRUE)
    as.numeric(sub(".*=", "", hit[[1]]))
  }
  for (cut in c("starts", "appearances")) {
    path <- file.path("out", paste0("club-seasons-", cut, ".csv"))
    second <- system2("Rscript", c("second-correlation.R", path), stdout = TRUE)
    saved <- utils::read.csv(file.path("out", paste0("correlations-", cut, ".csv")), stringsAsFactors = FALSE)
    summary <- lead_summary(saved)
    if (abs(grab(second, "median") - summary$median) > 1e-8) {
      stop("Second script median disagrees for ", cut)
    }
    if (abs(grab(second, "trimmed_mean") - summary$trimmed_mean) > 1e-8) {
      stop("Second script trimmed mean disagrees for ", cut)
    }
    if (abs(grab(second, "spearman") - summary$spearman) > 1e-8) {
      stop("Second script Spearman disagrees for ", cut)
    }
    boot <- utils::read.csv(file.path("out", paste0("bootstrap-", cut, ".csv")), stringsAsFactors = FALSE)
    percentile <- as.numeric(quantile(boot$median_correlation, 0.975, na.rm = TRUE, names = FALSE, type = 7))
    if (abs(grab(second, "percentile_97_5") - percentile) > 1e-6) {
      stop("Second script bootstrap percentile disagrees for ", cut)
    }
    message(cut, " lead numbers agree")
  }
  gaps <- utils::read.csv("out/points-reconciliation.csv", stringsAsFactors = FALSE)
  source("points.R")
  unexplained <- unexplained_points_gaps(gaps, named_deductions())
  if (nrow(unexplained) > 0) stop("Points reconciliation has unexplained gaps")
  if (length(unique(gaps$season_end)) != 31) stop("Points reconciliation is not 31 seasons")
  if (any(gaps$matches != 38)) stop("A club-season does not have 38 matches")
  message("points reconciliation ok")
}

message("verify ok")

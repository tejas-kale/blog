# Packages the analysis uses. worldfootballR is the GitHub build.
# Install into the library on R_LIBS, for example /tmp/r-lib.
#
#   mkdir -p /tmp/r-lib
#   R_LIBS=/tmp/r-lib Rscript notebooks/pl-squad-tenure-points/dependencies.R

lib <- Sys.getenv("R_LIBS", unset = "/tmp/r-lib")
dir.create(lib, recursive = TRUE, showWarnings = FALSE)
.libPaths(c(lib, .libPaths()))

cran <- c("ggplot2", "jsonlite", "svglite", "testthat")
missing <- cran[!vapply(cran, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing) > 0) {
  install.packages(missing, lib = lib, repos = "https://cloud.r-project.org")
}
if (!requireNamespace("remotes", quietly = TRUE)) {
  install.packages("remotes", lib = lib, repos = "https://cloud.r-project.org")
}
if (!requireNamespace("worldfootballR", quietly = TRUE)) {
  remotes::install_github("JaseZiv/worldfootballR", lib = lib, upgrade = "never")
}

# The plot file is checked against the saved club-season file.
# Changing one club's points must change the quoted correlation.
local({
  here <- "notebooks/pl-squad-tenure-points"
  if (!file.exists(file.path(here, "plotting.R"))) here <- "."
  source(file.path(here, "plotting.R"))

  original <- data.frame(
    club = "Alpha",
    season_end = 2010 + 1:10,
    median_tenure = 1:10,
    results_points = 2 * (1:10),
    stringsAsFactors = FALSE
  )
  tmp <- tempdir()
  path <- file.path(tmp, "export-fixture.csv")
  plot_path <- file.path(tmp, "export-fixture.svg")
  write.csv(original, path, row.names = FALSE)
  export_club_plot(path, "Alpha", plot_path)
  svg <- paste(readLines(plot_path, warn = FALSE), collapse = "\n")
  stopifnot(grepl("Pearson r = 1.000000", svg, fixed = TRUE))
  stopifnot(grepl("Season", svg, fixed = TRUE))

  shifted <- original
  shifted$results_points[[1]] <- 0
  shifted_path <- file.path(tmp, "export-shifted.csv")
  shifted_plot <- file.path(tmp, "export-shifted.svg")
  write.csv(shifted, shifted_path, row.names = FALSE)
  export_club_plot(shifted_path, "Alpha", shifted_plot)
  shifted_svg <- paste(readLines(shifted_plot, warn = FALSE), collapse = "\n")
  stopifnot(!grepl("Pearson r = 1.000000", shifted_svg, fixed = TRUE))
  cat("export ok\n")
})

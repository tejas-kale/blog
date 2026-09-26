plot_club_seasons <- function(club_seasons, club) {
  source_dir <- NULL
  d <- club_seasons[club_seasons$club == club, , drop = FALSE]
  d <- d[order(d$season_end), , drop = FALSE]
  r <- suppressWarnings(cor(d$median_tenure, d$results_points, method = "pearson"))
  d$season_label <- sprintf("%d\u2013%02d", d$season_end - 1L, d$season_end %% 100L)
  ggplot2::ggplot(d, ggplot2::aes(season_end, results_points)) +
    ggplot2::geom_line() +
    ggplot2::geom_point() +
    ggplot2::scale_x_continuous(
      name = "Season",
      breaks = d$season_end,
      labels = d$season_label
    ) +
    ggplot2::labs(
      y = "Results points",
      title = club,
      caption = sprintf("Pearson r = %.6f", r)
    )
}

export_club_plot <- function(club_season_file, club, path) {
  club_seasons <- utils::read.csv(club_season_file, stringsAsFactors = FALSE)
  plot <- plot_club_seasons(club_seasons, club)
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  ggplot2::ggsave(path, plot, width = 8, height = 4.5, device = svglite::svglite)
  invisible(path)
}

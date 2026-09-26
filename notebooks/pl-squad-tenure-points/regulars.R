regular_threshold <- function() 20L

regulars_for_cut <- function(player_seasons, cut) {
  if (!cut %in% c("starts", "appearances")) {
    stop("cut must be starts or appearances")
  }
  count <- player_seasons[[cut]]
  keep <- !is.na(count) & count >= regular_threshold()
  player_seasons[keep, , drop = FALSE]
}

club_season_median_tenure <- function(regulars) {
  if (nrow(regulars) == 0) {
    return(data.frame(
      club = character(),
      season_end = integer(),
      median_tenure = numeric(),
      n_regulars = integer(),
      stringsAsFactors = FALSE
    ))
  }
  keys <- paste(regulars$club, regulars$season_end, sep = "\r")
  split_rows <- split(regulars, keys)
  rows <- lapply(split_rows, function(d) {
    data.frame(
      club = d$club[[1]],
      season_end = d$season_end[[1]],
      median_tenure = median(d$tenure),
      n_regulars = nrow(d),
      stringsAsFactors = FALSE
    )
  })
  out <- do.call(rbind, rows)
  rownames(out) <- NULL
  out[order(out$club, out$season_end), , drop = FALSE]
}

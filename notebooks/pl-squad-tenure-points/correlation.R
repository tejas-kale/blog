# The lead number is the median of defined within-club Pearson correlations.
# Clubs with fewer than 10 seasons, and clubs whose median tenure does not
# vary, stay out of that median and are named. The bootstrap redraws seasons
# inside each club, seed 2026, 2000 replicates, tenure and points kept together.

within_club_correlations <- function(club_seasons, min_seasons = 10L) {
  clubs <- sort(unique(club_seasons$club))
  rows <- lapply(clubs, function(club) {
    d <- club_seasons[club_seasons$club == club, , drop = FALSE]
    n <- nrow(d)
    spearman <- NA_real_
    if (n < min_seasons) {
      reason <- "fewer than 10 seasons"
      r <- NA_real_
      defined <- FALSE
    } else if (length(unique(d$median_tenure)) < 2) {
      reason <- "median tenure does not vary"
      r <- NA_real_
      defined <- FALSE
    } else {
      r <- suppressWarnings(cor(d$median_tenure, d$results_points, method = "pearson"))
      defined <- is.finite(r)
      reason <- if (defined) "defined" else "undefined correlation"
      if (!defined) {
        r <- NA_real_
      } else {
        spearman <- suppressWarnings(cor(d$median_tenure, d$results_points, method = "spearman"))
        if (!is.finite(spearman)) spearman <- NA_real_
      }
    }
    data.frame(
      club = club,
      n_seasons = n,
      correlation = r,
      spearman = spearman,
      defined = defined,
      reason = reason,
      stringsAsFactors = FALSE
    )
  })
  out <- do.call(rbind, rows)
  rownames(out) <- NULL
  out
}

lead_summary <- function(correlations) {
  defined <- correlations[correlations$defined, , drop = FALSE]
  n_at_least_10 <- sum(correlations$n_seasons >= 10)
  undefined <- correlations[correlations$n_seasons >= 10 & !correlations$defined, , drop = FALSE]
  share <- if (n_at_least_10 == 0) NA_real_ else nrow(undefined) / n_at_least_10
  list(
    median = if (nrow(defined) == 0) NA_real_ else median(defined$correlation),
    trimmed_mean = if (nrow(defined) == 0) NA_real_ else mean(defined$correlation, trim = 0.1),
    spearman = if (nrow(defined) == 0) NA_real_ else median(defined$spearman, na.rm = TRUE),
    n_defined = nrow(defined),
    n_at_least_10 = n_at_least_10,
    undefined_share = share,
    undefined_clubs = sort(undefined$club),
    below_min_clubs = sort(correlations$club[correlations$n_seasons < 10])
  )
}

undefined_share_sentence <- function(summary) {
  if (is.na(summary$undefined_share) || summary$undefined_share <= 0.2) {
    return(NA_character_)
  }
  sprintf(
    "%d of %d clubs with at least 10 seasons are left out of the median, because their correlation is undefined. That is %d%%. The clubs are %s.",
    length(summary$undefined_clubs),
    summary$n_at_least_10,
    round(100 * summary$undefined_share),
    paste(summary$undefined_clubs, collapse = ", ")
  )
}

bootstrap_median_correlation <- function(club_seasons, n_replicates = 2000L, seed = 2026L, min_seasons = 10L) {
  counts <- table(club_seasons$club)
  clubs <- sort(names(counts)[counts >= min_seasons])
  by_club <- lapply(clubs, function(club) {
    d <- club_seasons[club_seasons$club == club, , drop = FALSE]
    d[order(d$season_end), , drop = FALSE]
  })
  names(by_club) <- clubs
  set.seed(seed)
  replicate_medians <- rep(NA_real_, n_replicates)
  club_draws <- matrix(NA_real_, nrow = n_replicates, ncol = length(clubs))
  colnames(club_draws) <- clubs
  for (i in seq_len(n_replicates)) {
    cors <- numeric()
    for (j in seq_along(clubs)) {
      d <- by_club[[j]]
      drawn <- d[sample.int(nrow(d), nrow(d), replace = TRUE), , drop = FALSE]
      if (length(unique(drawn$median_tenure)) < 2) next
      r <- suppressWarnings(cor(drawn$median_tenure, drawn$results_points, method = "pearson"))
      if (!is.finite(r)) next
      cors <- c(cors, r)
      club_draws[i, j] <- r
    }
    if (length(cors) > 0) replicate_medians[[i]] <- median(cors)
  }
  interval <- as.numeric(quantile(replicate_medians, c(0.025, 0.975), na.rm = TRUE, names = FALSE, type = 7))
  club_intervals <- data.frame(
    club = clubs,
    low = vapply(clubs, function(club) {
      as.numeric(quantile(club_draws[, club], 0.025, na.rm = TRUE, names = FALSE, type = 7))
    }, numeric(1)),
    high = vapply(clubs, function(club) {
      as.numeric(quantile(club_draws[, club], 0.975, na.rm = TRUE, names = FALSE, type = 7))
    }, numeric(1)),
    stringsAsFactors = FALSE
  )
  list(
    replicate_medians = replicate_medians,
    interval = interval,
    club_intervals = club_intervals
  )
}

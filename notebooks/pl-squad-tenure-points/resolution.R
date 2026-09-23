# The org table is read and not rewritten. A filled row overrides the
# automatic matcher. match lets the player into the median. exclude keeps
# the player out. Ambiguous and unmatched players stay out until then.
# A club-season with any regular still out is absent from the correlation.

apply_org_resolution <- function(regulars, org_table) {
  regulars$enters <- FALSE
  regulars$tm_id <- as.character(regulars$tm_id)
  if (nrow(org_table) > 0) org_table$tm_id <- as.character(org_table$tm_id)
  for (i in seq_len(nrow(regulars))) {
    hit <- org_table$season_end == regulars$season_end[[i]] &
      org_table$club == regulars$club[[i]] &
      org_table$source_name == regulars$source_name[[i]]
    if (any(hit)) {
      row <- org_table[which(hit)[[1]], ]
      if (row$resolution == "exclude") {
        regulars$enters[[i]] <- FALSE
      } else if (row$resolution == "match") {
        regulars$enters[[i]] <- TRUE
        regulars$fbref_id[[i]] <- row$fbref_id
        regulars$tm_id[[i]] <- row$tm_id
      } else {
        stop("resolution must be match or exclude")
      }
    } else {
      regulars$enters[[i]] <- regulars$auto_status[[i]] == "unique"
    }
  }
  regulars
}

club_seasons_blocked_by_unresolved <- function(regulars) {
  keys <- paste(regulars$club, regulars$season_end, sep = "\r")
  blocked <- vapply(split(regulars, keys), function(d) any(!d$enters), logical(1))
  blocked_keys <- names(blocked)[blocked]
  if (length(blocked_keys) == 0) {
    return(data.frame(club = character(), season_end = integer(), stringsAsFactors = FALSE))
  }
  data.frame(
    club = sub("\r.*", "", blocked_keys),
    season_end = as.integer(sub(".*\r", "", blocked_keys)),
    stringsAsFactors = FALSE
  )
}

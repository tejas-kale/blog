# Results points are 3 for a win and 1 for a draw. Official table points can
# be lower. The gap is official minus results. Named deductions are the only
# accepted gaps. Everton 2023-24 is -8: the 10-point deduction was reduced to
# 6, and the further 2 stood after the club withdrew the appeal.

canonical_club <- function(name) {
  name <- sub(" [(].*$", "", name)
  name <- sub(" [Ff][Cc]$", "", name)
  name <- sub(" [Aa][Ff][Cc]$", "", name)
  cleaned <- tolower(iconv(enc2utf8(name), to = "ASCII//TRANSLIT"))
  key <- gsub("[^a-z0-9]", "", cleaned)
  map <- c(
    arsenal = "Arsenal",
    astonvilla = "Aston Villa",
    barnsley = "Barnsley",
    birmingham = "Birmingham City",
    birminghamcity = "Birmingham City",
    blackburn = "Blackburn Rovers",
    blackburnrovers = "Blackburn Rovers",
    blackpool = "Blackpool",
    bolton = "Bolton Wanderers",
    boltonwanderers = "Bolton Wanderers",
    bournemouth = "Bournemouth",
    afcbournemouth = "Bournemouth",
    bradford = "Bradford City",
    bradfordcity = "Bradford City",
    brentford = "Brentford",
    brighton = "Brighton and Hove Albion",
    brightonandhovealbion = "Brighton and Hove Albion",
    brightonhovealbion = "Brighton and Hove Albion",
    burnley = "Burnley",
    cardiff = "Cardiff City",
    cardiffcity = "Cardiff City",
    charlton = "Charlton Athletic",
    charltonath = "Charlton Athletic",
    charltonathletic = "Charlton Athletic",
    chelsea = "Chelsea",
    coventry = "Coventry City",
    coventrycity = "Coventry City",
    crystalpalace = "Crystal Palace",
    derby = "Derby County",
    derbycounty = "Derby County",
    everton = "Everton",
    fulham = "Fulham",
    huddersfield = "Huddersfield Town",
    huddersfieldtown = "Huddersfield Town",
    hull = "Hull City",
    hullcity = "Hull City",
    ipswich = "Ipswich Town",
    ipswichtown = "Ipswich Town",
    leeds = "Leeds United",
    leedsunited = "Leeds United",
    leicester = "Leicester City",
    leicestercity = "Leicester City",
    liverpool = "Liverpool",
    luton = "Luton Town",
    lutontown = "Luton Town",
    mancity = "Manchester City",
    manchestercity = "Manchester City",
    manunited = "Manchester United",
    manchesterutd = "Manchester United",
    manchesterunited = "Manchester United",
    middlesbrough = "Middlesbrough",
    newcastle = "Newcastle United",
    newcastleutd = "Newcastle United",
    newcastleunited = "Newcastle United",
    norwich = "Norwich City",
    norwichcity = "Norwich City",
    nottmforest = "Nottingham Forest",
    notthamforest = "Nottingham Forest",
    nottingham = "Nottingham Forest",
    nottinghamforest = "Nottingham Forest",
    portsmouth = "Portsmouth",
    qpr = "Queens Park Rangers",
    queensparkrangers = "Queens Park Rangers",
    reading = "Reading",
    sheffieldunited = "Sheffield United",
    sheffieldutd = "Sheffield United",
    sheffieldwednesday = "Sheffield Wednesday",
    sheffieldweds = "Sheffield Wednesday",
    southampton = "Southampton",
    stoke = "Stoke City",
    stokecity = "Stoke City",
    sunderland = "Sunderland",
    swansea = "Swansea City",
    swanseacity = "Swansea City",
    tottenham = "Tottenham Hotspur",
    tottenhamhotspur = "Tottenham Hotspur",
    spurs = "Tottenham Hotspur",
    watford = "Watford",
    westbrom = "West Bromwich Albion",
    westbromwichalbion = "West Bromwich Albion",
    westham = "West Ham United",
    westhamunited = "West Ham United",
    wigan = "Wigan Athletic",
    wiganathletic = "Wigan Athletic",
    wimbledon = "Wimbledon",
    wolves = "Wolverhampton Wanderers",
    wolverhamptonwanderers = "Wolverhampton Wanderers"
  )
  if (!key %in% names(map)) stop("Unmapped club: ", name, " key=", key)
  unname(map[[key]])
}

named_deductions <- function() {
  data.frame(
    club = c("Middlesbrough", "Portsmouth", "Everton", "Nottingham Forest"),
    season_end = c(1997L, 2010L, 2024L, 2024L),
    deduction = c(-3L, -9L, -8L, -4L),
    stringsAsFactors = FALSE
  )
}

results_points_from_matches <- function(matches) {
  if (!all(c("HomeTeam", "AwayTeam", "FTR") %in% names(matches))) {
    stop("matches need HomeTeam, AwayTeam, and FTR")
  }
  home_points <- ifelse(matches$FTR == "H", 3L, ifelse(matches$FTR == "D", 1L, 0L))
  away_points <- ifelse(matches$FTR == "A", 3L, ifelse(matches$FTR == "D", 1L, 0L))
  long <- rbind(
    data.frame(club = matches$HomeTeam, points = home_points, stringsAsFactors = FALSE),
    data.frame(club = matches$AwayTeam, points = away_points, stringsAsFactors = FALSE)
  )
  clubs <- sort(unique(long$club))
  data.frame(
    club = clubs,
    points = vapply(clubs, function(club) sum(long$points[long$club == club]), integer(1)),
    matches = vapply(clubs, function(club) sum(long$club == club), integer(1)),
    stringsAsFactors = FALSE
  )
}

unexplained_points_gaps <- function(gaps, deductions) {
  if (!all(c("club", "season_end", "gap") %in% names(gaps))) {
    stop("gaps need club, season_end, and gap")
  }
  explained <- function(i) {
    if (gaps$gap[[i]] == 0) return(TRUE)
    hit <- deductions$club == gaps$club[[i]] &
      deductions$season_end == gaps$season_end[[i]] &
      deductions$deduction == gaps$gap[[i]]
    any(hit)
  }
  gaps[!vapply(seq_len(nrow(gaps)), explained, logical(1)), , drop = FALSE]
}

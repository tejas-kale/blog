# Seam: the hand-worked tenure sheet. Expected seasons were read off Transfermarkt,
# not off the code. Harry Kane, player id 132098.
local({
  here <- "notebooks/pl-squad-tenure-points"
  if (!file.exists(file.path(here, "tenure.R"))) here <- "."
  source(file.path(here, "tenure.R"))

  sheet <- read.csv(file.path(here, "hand-worked-tenure.csv"), stringsAsFactors = FALSE)
  transfers <- read.csv(file.path(here, "kane-transfers.csv"), stringsAsFactors = FALSE)
  spells <- involvement_from_transfers(transfers, through_season_end = 2026L)
  tenured <- senior_squad_tenure(spells)

  same_number <- function(got, expected) {
    if (is.na(expected) && is.na(got)) return(TRUE)
    if (is.na(expected) || is.na(got)) return(FALSE)
    abs(got - expected) < 1e-9
  }

  for (i in seq_len(nrow(sheet))) {
    row <- sheet[i, ]
    hit <- tenured$player_id == row$player_id &
      tenured$season_end == row$season_end &
      tenured$club == row$club &
      tenured$involvement == row$involvement
    if (sum(hit) != 1) {
      stop(
        "Sheet row not reproduced: ", row$season_end, " ", row$club,
        " ", row$involvement, " matches=", sum(hit)
      )
    }
    if (!same_number(tenured$tenure[hit], row$tenure)) {
      stop(
        "Tenure mismatch ", row$season_end, " ", row$club,
        " expected ", row$tenure, " got ", tenured$tenure[hit]
      )
    }
  }

  # Full-season loan wipes the parent. A later season starts at 1.
  wipe <- data.frame(
    player_id = "wipe",
    date = c("2017-07-01", "2018-09-01", "2019-06-01"),
    club_from = c("Youth", "Parent", "LoanClub"),
    club_to = c("Parent", "LoanClub", "Parent"),
    transfer_type = c("senior", "loan", "end_loan"),
    stringsAsFactors = FALSE
  )
  wipe_tenure <- senior_squad_tenure(involvement_from_transfers(wipe, 2020L))
  expect_tenure <- function(season_end, club, involvement, tenure) {
    hit <- wipe_tenure$season_end == season_end &
      wipe_tenure$club == club &
      wipe_tenure$involvement == involvement
    if (sum(hit) != 1 || !same_number(wipe_tenure$tenure[hit], tenure)) {
      stop("Wipe case failed: ", season_end, " ", club, " ", involvement,
           " got ", paste(wipe_tenure$tenure[hit], collapse = ","))
    }
  }
  expect_tenure(2018, "Parent", "senior", 1)
  expect_tenure(2019, "Parent", "full_loan_out", 0)
  expect_tenure(2019, "LoanClub", "full_loan_in", 1)
  expect_tenure(2020, "Parent", "senior", 1)

  # Mid-season permanent move, then a later return starts at 1.
  moved <- data.frame(
    player_id = "move",
    date = c("2016-07-01", "2018-01-15", "2019-07-01"),
    club_from = c("Youth", "A", "B"),
    club_to = c("A", "B", "A"),
    transfer_type = c("senior", "permanent", "permanent"),
    stringsAsFactors = FALSE
  )
  moved_tenure <- senior_squad_tenure(involvement_from_transfers(moved, 2020L))
  expect_move <- function(season_end, club, involvement, tenure) {
    hit <- moved_tenure$season_end == season_end &
      moved_tenure$club == club &
      moved_tenure$involvement == involvement
    if (sum(hit) != 1 || !same_number(moved_tenure$tenure[hit], tenure)) {
      print(moved_tenure)
      stop("Move case failed: ", season_end, " ", club, " ", involvement,
           " got ", paste(moved_tenure$tenure[hit], collapse = ","))
    }
  }
  expect_move(2017, "A", "senior", 1)
  expect_move(2018, "A", "mid_move_out", 1.5)
  expect_move(2018, "B", "mid_move_in", 0.5)
  expect_move(2019, "B", "senior", 1.5)
  expect_move(2020, "A", "senior", 1)

  # A loan that becomes permanent at the same club covers the whole campaign.
  converted <- data.frame(
    player_id = "convert",
    date = c("2010-07-01", "2010-09-01", "2010-10-01"),
    club_from = c("Youth", "Parent", "Parent"),
    club_to = c("Parent", "LoanClub", "LoanClub"),
    transfer_type = c("senior", "loan", "permanent"),
    stringsAsFactors = FALSE
  )
  converted_tenure <- senior_squad_tenure(involvement_from_transfers(converted, 2011L))
  expect_converted <- function(season_end, club, involvement, tenure) {
    hit <- converted_tenure$season_end == season_end &
      converted_tenure$club == club &
      converted_tenure$involvement == involvement
    if (sum(hit) != 1 || !same_number(converted_tenure$tenure[hit], tenure)) {
      print(converted_tenure)
      stop("Converted loan failed: ", season_end, " ", club, " ", involvement)
    }
  }
  expect_converted(2011, "LoanClub", "senior", 1)
  expect_converted(2011, "Parent", "full_loan_out", 0)

  # Loan from the campaign's first day, then a sale to a third club.
  sold <- data.frame(
    player_id = "sold",
    date = c("2016-07-01", "2016-09-01", "2016-11-01", "2016-11-01"),
    club_from = c("Youth", "A", "L", "A"),
    club_to = c("A", "L", "A", "B"),
    transfer_type = c("senior", "loan", "end_loan", "permanent"),
    stringsAsFactors = FALSE
  )
  sold_tenure <- senior_squad_tenure(involvement_from_transfers(sold, 2017L))
  expect_sold <- function(season_end, club, involvement, tenure) {
    hit <- sold_tenure$season_end == season_end &
      sold_tenure$club == club &
      sold_tenure$involvement == involvement
    if (sum(hit) != 1 || !same_number(sold_tenure$tenure[hit], tenure)) {
      print(sold_tenure)
      stop("Sold-on loan failed: ", season_end, " ", club, " ", involvement)
    }
  }
  expect_sold(2017, "L", "mid_loan_in", 0.5)
  expect_sold(2017, "B", "mid_move_in", 0.5)
  expect_sold(2017, "A", "mid_move_out", 0.5)

  # Two loan clubs and no senior days: the parent gets 0.5 once, each loan club 0.5.
  two_loans <- data.frame(
    player_id = "twoloan",
    date = c("2012-07-01", "2012-09-01", "2013-01-15", "2013-01-15"),
    club_from = c("Youth", "Parent", "LoanA", "Parent"),
    club_to = c("Parent", "LoanA", "Parent", "LoanB"),
    transfer_type = c("senior", "loan", "end_loan", "loan"),
    stringsAsFactors = FALSE
  )
  two_tenure <- senior_squad_tenure(involvement_from_transfers(two_loans, 2013L))
  expect_two <- function(season_end, club, involvement, tenure) {
    hit <- two_tenure$season_end == season_end &
      two_tenure$club == club &
      two_tenure$involvement == involvement
    if (sum(hit) != 1 || !same_number(two_tenure$tenure[hit], tenure)) {
      print(two_tenure)
      stop("Two-loan case failed: ", season_end, " ", club, " ", involvement)
    }
  }
  expect_two(2013, "Parent", "mid_loan_parent", 0.5)
  expect_two(2013, "LoanA", "mid_loan_in", 0.5)
  expect_two(2013, "LoanB", "mid_loan_in", 0.5)

  cat("tenure sheet ok\n")
})

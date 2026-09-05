#!/usr/bin/env python3
"""Build a small DuckDB extract from the official CPS basic monthly files.

The raw files are deliberately downloaded to a cache outside the repository.
Run with ``uv run --with duckdb scripts/build_data_scientist_dataset.py``.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import re
import urllib.request
import zipfile
from pathlib import Path

import duckdb


CENSUS_ROOT = "https://www2.census.gov/programs-surveys/cps/datasets"
OCCUPATION_CODE = "1240"
OCCUPATION_TITLE = "Other mathematical science occupations (includes data scientists)"
START = dt.date(2020, 1, 1)
OEWS = [
    (2021, 5, "15-2051", 105_980, None, "https://www.bls.gov/oes/2021/may/oes_nat.htm"),
    (2022, 5, "15-2051", 159_630, None, "https://www.bls.gov/oes/2022/may/oes_nat.htm"),
    (2023, 5, "15-2051", 192_710, 1.2, "https://www.bls.gov/oes/2023/may/oes_nat.htm"),
    (2024, 5, "15-2051", 233_440, None, "https://www.bls.gov/oes/2024/may/oes_nat.htm"),
    (2025, 5, "15-2051", 262_440, None, "https://www.bls.gov/oes/2025/may/oes_nat.htm"),
]


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "data-scientist-dataset/1.0"})
    with urllib.request.urlopen(request) as response:
        return response.read()


def available_files(year: int) -> list[tuple[int, str]]:
    html = fetch(f"{CENSUS_ROOT}/{year}/basic/").decode("utf-8", errors="replace")
    found = re.findall(r"href=\"([a-z]{3})(\d{2})pub\.zip\"", html, flags=re.I)
    months = {dt.datetime.strptime(month, "%b").month: f"{month}{yy}pub.zip" for month, yy in found}
    return sorted(months.items())


def iter_rows(payload: bytes):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not names:
            raise ValueError(f"No CSV file in {archive.namelist()!r}")
        with archive.open(names[0]) as raw:
            yield from csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", newline=""))


def extract_month(year: int, month: int, archive: Path) -> tuple[int, float]:
    payload = archive.read_bytes()
    count = 0
    estimate = 0.0
    for row in iter_rows(payload):
        # PTIO1OCD is the primary-job occupation; PREMPNOT=1 is employed.
        if row.get("PREMPNOT") != "1" or row.get("PTIO1OCD", "").zfill(4) != OCCUPATION_CODE:
            continue
        count += 1
        estimate += float(row["PWSSWGT"]) / 10_000
    return count, estimate


def download_month(year: int, month: int, filename: str, cache: Path) -> Path:
    target = cache / str(year) / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(fetch(f"{CENSUS_ROOT}/{year}/basic/{filename}"))
    return target


def build(database: Path, cache: Path, start: dt.date, end: dt.date | None) -> None:
    extraction_date = dt.date.today().isoformat()
    rows: list[tuple] = []
    for year in range(start.year, (end or dt.date.today()).year + 1):
        for month, filename in available_files(year):
            reference = dt.date(year, month, 1)
            if reference < start or (end and reference > end):
                continue
            archive = download_month(year, month, filename, cache)
            count, estimate = extract_month(year, month, archive)
            rows.append((reference, OCCUPATION_CODE, OCCUPATION_TITLE, count, estimate,
                         None, None, filename, year, extraction_date,
                         hashlib.sha256(archive.read_bytes()).hexdigest()))

    con = duckdb.connect(str(database))
    con.execute("DROP TABLE IF EXISTS monthly_cps")
    con.execute("DROP TABLE IF EXISTS annual_oews")
    con.execute("DROP TABLE IF EXISTS methodology")
    con.execute("""CREATE TABLE monthly_cps (
        month DATE, occupation_code VARCHAR, occupation_title VARCHAR,
        unweighted_respondent_count INTEGER, weighted_employment_estimate DOUBLE,
        standard_error DOUBLE, confidence_interval_95 VARCHAR, source_file VARCHAR,
        vintage INTEGER, extraction_date DATE, source_sha256 VARCHAR)""")
    con.executemany("INSERT INTO monthly_cps VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    con.execute("""CREATE TABLE annual_oews (
        reference_year INTEGER, reference_month INTEGER, soc_code VARCHAR,
        employment_estimate INTEGER, relative_standard_error_percent DOUBLE,
        source_url VARCHAR, extraction_date DATE)""")
    con.executemany("INSERT INTO annual_oews VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [row + (extraction_date,) for row in OEWS])
    con.execute("""CREATE TABLE methodology (
        source VARCHAR, definition VARCHAR, classification VARCHAR,
        weighting VARCHAR, comparability VARCHAR, known_limitations VARCHAR)""")
    con.execute("INSERT INTO methodology VALUES (?, ?, ?, ?, ?, ?)", (
        "CPS basic monthly public-use microdata",
        "Employed people whose primary-job Census occupation code is 1240.",
        "2018 Census occupation classification; code 1240 is a combined category that includes data scientists and other mathematical-science occupations.",
        "Sum PWSSWGT / 10,000 for PREMPNOT=1 respondents.",
        "Comparable from January 2020 classification-wise; annual CPS tables publish the combined category, not a standalone data-scientist series.",
        "Public-use weights differ slightly from BLS internal weights; no replicate weights are included in the basic files, so standard errors are NULL. OEWS measures establishment jobs and excludes self-employed workers.",
    ))
    con.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("data/data_scientists.duckdb"))
    parser.add_argument("--cache", type=Path, default=Path("/tmp/cps-basic-cache"))
    parser.add_argument("--start", type=lambda value: dt.date.fromisoformat(value), default=START)
    parser.add_argument("--end", type=lambda value: dt.date.fromisoformat(value))
    args = parser.parse_args()
    args.database.parent.mkdir(parents=True, exist_ok=True)
    build(args.database, args.cache, args.start, args.end)


if __name__ == "__main__":
    main()

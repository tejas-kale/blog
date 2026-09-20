#!/usr/bin/env python3
"""Build a long OEWS panel for the Economist Chart 3 occupations.

National HTML tables are blocked on bls.gov from this environment, so files
are read from the Wayback Machine and cached next to this script.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
OUT = HERE / "oews_occupations.csv"
UA = "data-scientist-notebook/2.0 (https://github.com/tejas-kale/blog)"

OCCUPATIONS = [
    {"occupation": "Data scientists", "soc": "15-2051", "codes": ("15-2051",)},
    {"occupation": "Financial analysts", "soc": "13-2051", "codes": ("13-2051",)},
    {"occupation": "Paralegals", "soc": "23-2011", "codes": ("23-2011",)},
    {
        "occupation": "Info-security analysts",
        "soc": "15-1212",
        "codes": ("15-1212", "15-1122"),
    },
    {
        "occupation": "Market-research analysts",
        "soc": "13-1161",
        "codes": ("13-1161", "19-3021"),
    },
    {"occupation": "Lawyers", "soc": "23-1011", "codes": ("23-1011",)},
    {"occupation": "Translators", "soc": "27-3091", "codes": ("27-3091",)},
    {"occupation": "Writers & authors", "soc": "27-3043", "codes": ("27-3043",)},
    {"occupation": "Graphic designers", "soc": "27-1024", "codes": ("27-1024",)},
    {"occupation": "Bookkeeping clerks", "soc": "43-3031", "codes": ("43-3031",)},
    {"occupation": "Customer-service reps", "soc": "43-4051", "codes": ("43-4051",)},
    {"occupation": "Data-entry keyers", "soc": "43-9021", "codes": ("43-9021",)},
]

WANTED = {code for occ in OCCUPATIONS for code in occ["codes"]} | {"15-2098"}
HYBRID_DS = "15-2098"

NAT_URLS = [
    "https://www.bls.gov/oes/{year}/may/oes_nat.htm",
    "http://www.bls.gov/oes/{year}/may/oes_nat.htm",
    "https://www.bls.gov/oes/{year}/oes_nat.htm",
    "http://www.bls.gov/oes/{year}/oes_nat.htm",
]

GROUP_FILES = (
    "oes_13Bu.htm",
    "oes_15Co.htm",
    "oes_19Li.htm",
    "oes_23Le.htm",
    "oes_27Ar.htm",
    "oes_43Of.htm",
)

SOC_CELL = re.compile(r"^\d{2}-\d{4}$")
INT_CELL = re.compile(r"^[0-9][0-9,]+$")


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "tr":
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._row is not None and self._cell is not None:
            self._row.append(re.sub(r"\s+", " ", "".join(self._cell)).strip())
            self._cell = None
        elif tag == "tr" and self._row:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)


def fetch(url: str, timeout: int = 45) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def cdx_best(original: str) -> str | None:
    query = (
        "https://web.archive.org/cdx/search/cdx?"
        f"url={urllib.parse.quote(original, safe='')}&"
        "output=json&fl=timestamp,original,statuscode,length&"
        "filter=statuscode:200&limit=30"
    )
    try:
        rows = json.loads(fetch(query, timeout=25).decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    scored = []
    for row in rows[1:]:
        ts, orig, status, length = row[:4]
        if status != "200":
            continue
        try:
            nbytes = int(length or 0)
        except ValueError:
            nbytes = 0
        scored.append((nbytes, ts, orig))
    if not scored:
        return None
    scored.sort(reverse=True)
    _, ts, orig = scored[0]
    return f"https://web.archive.org/web/{ts}/{orig}"


def download(url: str) -> bytes | None:
    try:
        raw = fetch(url)
    except (urllib.error.URLError, TimeoutError):
        return None
    if len(raw) < 5_000 or b"Access Denied" in raw[:800]:
        return None
    return raw


def parse_tables(raw: bytes) -> dict[str, tuple[str, int]]:
    parser = TableParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    found: dict[str, tuple[str, int]] = {}
    for row in parser.rows:
        if not row or not SOC_CELL.match(row[0]):
            continue
        code = row[0]
        if code not in WANTED or code in found:
            continue
        title = row[1] if len(row) > 1 else ""
        employment = None
        for cell in row[2:]:
            if cell.lower() in {"detail", "major", "minor", "broad"}:
                continue
            if "%" in cell or cell.startswith("$") or "." in cell:
                continue
            if INT_CELL.match(cell):
                employment = int(cell.replace(",", ""))
                break
        if employment is None:
            continue
        found[code] = (title, employment)
    return found


def is_index(raw: bytes) -> bool:
    text = raw.decode("utf-8", errors="replace").lower()
    return "divided into twenty-two tables" in text or "oes_23le.htm" in text.lower()


def cache_path(name: str) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    return CACHE / name


def load_cached_or_fetch(name: str, originals: list[str]) -> tuple[str, bytes]:
    html_path = cache_path(name)
    url_path = cache_path(name.replace(".html", ".url"))
    if html_path.exists() and html_path.stat().st_size > 5_000:
        source = url_path.read_text().strip() if url_path.exists() else "cache"
        return source, html_path.read_bytes()
    last_error = "no snapshot"
    for original in originals:
        source = cdx_best(original)
        if not source:
            continue
        raw = download(source)
        if raw is None:
            last_error = f"empty {source}"
            continue
        html_path.write_bytes(raw)
        url_path.write_text(source + "\n")
        return source, raw
        time.sleep(0.2)
    raise RuntimeError(f"{name}: {last_error}")


def load_year(year: int) -> tuple[str, dict[str, tuple[str, int]]]:
    originals = [template.format(year=year) for template in NAT_URLS]
    source, raw = load_cached_or_fetch(f"oes_nat_{year}.html", originals)
    found = parse_tables(raw)
    if found and not is_index(raw):
        return source, found

    # 1999–2004 publish one HTML table per SOC major group.
    combined: dict[str, tuple[str, int]] = {}
    sources = [source]
    year_dir = "may/" if year >= 2003 else ""
    for group in GROUP_FILES:
        group_originals = [
            f"https://www.bls.gov/oes/{year}/{year_dir}{group}",
            f"http://www.bls.gov/oes/{year}/{year_dir}{group}",
            f"https://www.bls.gov/oes/{year}/{group}",
            f"http://www.bls.gov/oes/{year}/{group}",
        ]
        try:
            group_source, group_raw = load_cached_or_fetch(
                f"{year}_{group}", group_originals
            )
        except RuntimeError as exc:
            print(f"  skip {year} {group}: {exc}")
            continue
        sources.append(group_source)
        combined.update(parse_tables(group_raw))
        time.sleep(0.15)
    if not combined:
        raise RuntimeError(f"no occupation rows for {year}")
    return sources[0], combined


TABLE1_PATTERNS = {
    "Data scientists": "Data scientists",
    "Financial analysts": "Financial and investment analysts",
    "Paralegals": "Paralegals and legal assistants",
    "Info-security analysts": "Information security analysts",
    "Market-research analysts": "Market research analysts and marketing specialists",
    "Lawyers": "Lawyers",
    "Translators": "Interpreters and translators",
    "Writers & authors": "Writers and authors",
    "Graphic designers": "Graphic designers",
    "Bookkeeping clerks": "Bookkeeping, accounting, and auditing clerks",
    "Customer-service reps": "Customer service representatives",
    "Data-entry keyers": "Data entry keyers",
}


def parse_table1(raw: bytes) -> dict[str, int]:
    page = raw.decode("utf-8", errors="replace")
    page = re.sub(r"(?is)<script.*?</script>", " ", page)
    page = re.sub(r"(?is)<style.*?</style>", " ", page)
    page = re.sub(r"<[^>]+>", " ", page)
    page = page.replace("\xa0", " ")
    found: dict[str, int] = {}
    for occupation, pattern in TABLE1_PATTERNS.items():
        escaped = re.sub(r"([.,])", r"\\\1", pattern)
        match = re.search(rf"(?i){escaped}\.{{3,}}\s*([0-9,]+)", page)
        if match:
            found[occupation] = int(match.group(1).replace(",", ""))
    return found


def emit_rows(year: int, source: str, found: dict[str, tuple[str, int]]) -> list[dict]:
    rows = []
    for occ in OCCUPATIONS:
        match = next(((code, *found[code]) for code in occ["codes"] if code in found), None)
        if match is None:
            continue
        code, title, employment = match
        rows.append(
            {
                "year": year,
                "month": 5,
                "occupation": occ["occupation"],
                "soc": occ["soc"],
                "soc_in_release": code,
                "title_in_release": title,
                "employment": employment,
                "source_url": source,
            }
        )
    return rows


def load_local_year(year: int) -> tuple[str, dict[str, tuple[str, int]]] | None:
    nat = cache_path(f"oes_nat_{year}.html")
    url_path = cache_path(f"oes_nat_{year}.url")
    found: dict[str, tuple[str, int]] = {}
    source = url_path.read_text().strip() if url_path.exists() else "cache"
    if nat.exists() and nat.stat().st_size > 20_000:
        raw = nat.read_bytes()
        if not is_index(raw):
            parsed = parse_tables(raw)
            if parsed:
                return source, parsed
    for group in GROUP_FILES:
        group_path = cache_path(f"{year}_{group}")
        if not group_path.exists():
            continue
        found.update(parse_tables(group_path.read_bytes()))
    if found:
        return source, found
    return None


def build_local() -> None:
    """Assemble the panel from cached HTML only (no network)."""
    rows: list[dict] = []
    for year in range(1999, 2026):
        loaded = load_local_year(year)
        if loaded is None:
            print(f"{year}: no local table", flush=True)
            continue
        source, found = loaded
        print(f"{year}: {len(found)} codes", flush=True)
        rows.extend(emit_rows(year, source, found))

    soc = {occ["occupation"]: occ["soc"] for occ in OCCUPATIONS}
    for year in (2024, 2025):
        table1 = cache_path(f"ocwage_{year}.html")
        if not table1.exists():
            continue
        source = (
            cache_path(f"ocwage_{year}.url").read_text().strip()
            if cache_path(f"ocwage_{year}.url").exists()
            else f"BLS OEWS Table 1 {year}"
        )
        parsed = parse_table1(table1.read_bytes())
        print(f"{year} Table 1: {len(parsed)} occupations", flush=True)
        for occupation, employment in parsed.items():
            rows.append(
                {
                    "year": year,
                    "month": 5,
                    "occupation": occupation,
                    "soc": soc[occupation],
                    "soc_in_release": soc[occupation],
                    "title_in_release": TABLE1_PATTERNS[occupation],
                    "employment": employment,
                    "source_url": source,
                }
            )

    if not rows:
        raise SystemExit("no rows parsed")
    # Prefer a later source in the same year/occupation (Table 1 over a stub).
    latest: dict[tuple[str, int], dict] = {}
    for row in rows:
        latest[(row["occupation"], row["year"])] = row
    rows = sorted(latest.values(), key=lambda item: (item["occupation"], item["year"]))
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT}", flush=True)


def main() -> None:
    build_local()


if __name__ == "__main__":
    main()

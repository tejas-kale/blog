#!/usr/bin/env python3
"""Save Premier League pages for the tenure analysis.

Raw vendor HTML and CSV stay under raw/ and are not published.
Live FBref returned a Cloudflare challenge to curl and to headless Chrome.
These FBref tables are Wayback captures of the same competition URLs.
"""

import csv
import gzip
import html
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
PAUSE = 1.0
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "identity"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        raw = response.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw


def fetch_text(url):
    raw = fetch(url)
    for encoding in ("utf-8", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def pause():
    time.sleep(PAUSE)


def season_label(end_year):
    return f"{end_year - 1}-{end_year}"


def football_data_code(end_year):
    return f"{(end_year - 1) % 100:02d}{end_year % 100:02d}"


def wayback_url(original):
    available = "https://archive.org/wayback/available?url=" + urllib.request.quote(original, safe="")
    try:
        payload = json.loads(fetch_text(available))
    except Exception:
        return None
    snap = payload.get("archived_snapshots", {}).get("closest")
    if not snap or not snap.get("available"):
        return None
    return snap["timestamp"]


def cdx_timestamps(original):
    hostpath = original.split("://", 1)[1]
    query = (
        "https://web.archive.org/cdx/search/cdx?url="
        + urllib.request.quote(hostpath, safe="")
        + "&output=json&fl=timestamp,statuscode&filter=statuscode:200"
    )
    for attempt in range(4):
        try:
            rows = json.loads(fetch_text(query))
            break
        except Exception:
            time.sleep(2 ** attempt)
    else:
        return []
    if len(rows) <= 1:
        return []
    return [row[0] for row in rows[1:]]


def try_timestamps(original, timestamps, errors):
    for timestamp in timestamps:
        for prefix in (
            f"https://web.archive.org/web/{timestamp}id_/",
            f"https://web.archive.org/web/{timestamp}/",
        ):
            url = prefix + original
            try:
                text = fetch_text(url)
            except Exception as error:
                errors.append(f"{url} {error}")
                pause()
                continue
            if "Just a moment" in text[:500] or len(text) < 1000:
                errors.append(f"thin capture {url}")
                continue
            return text, timestamp, original
    return None


def download_archived(candidates):
    errors = []
    for candidate in candidates:
        timestamp = wayback_url(candidate)
        pause()
        if not timestamp:
            continue
        got = try_timestamps(candidate, [timestamp], errors)
        if got:
            return got
    for candidate in candidates:
        got = try_timestamps(candidate, list(reversed(cdx_timestamps(candidate))), errors)
        if got:
            return got
    raise SystemExit("Wayback download failed: " + "; ".join(errors[:8]))


def strip_tags(value):
    text = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", text).strip()


def cell(row, stat):
    match = re.search(rf'data-stat="{stat}"[^>]*>(.*?)</t[dh]>', row, flags=re.S)
    if not match:
        return ""
    return strip_tags(match.group(1))


def save_matches(end_years):
    out = RAW / "matches"
    out.mkdir(parents=True, exist_ok=True)
    for end_year in end_years:
        dest = out / f"{end_year}.csv"
        if dest.exists() and dest.stat().st_size > 100:
            continue
        code = football_data_code(end_year)
        url = f"https://www.football-data.co.uk/mmz4281/{code}/E0.csv"
        raw = fetch(url)
        if raw.startswith(b"\xef\xbb\xbf"):
            raw = raw[3:]
        dest.write_bytes(raw)
        print("match", end_year, dest.stat().st_size, flush=True)
        pause()


def parse_league_table(html):
    match = re.search(r'<table[^>]*id="results[^"]*_overall".*?</table>', html, flags=re.S)
    if not match:
        return []
    rows = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", match.group(0), flags=re.S):
        team = cell(row, "team") or cell(row, "squad")
        points = cell(row, "points")
        games = cell(row, "games")
        if not team or team in {"Squad", "Team"} or not points.isdigit():
            continue
        rows.append({"team": team, "points": int(points), "games": int(games) if games.isdigit() else None})
    return rows


def league_player_table(html):
    ids = re.findall(r'<table[^>]*id="(stats_standard_\d+)"', html)
    if "stats_standard_9" in ids:
        ids = ["stats_standard_9"]
    best = None
    for table_id in ids:
        match = re.search(rf'<table[^>]*id="{table_id}".*?</table>', html, flags=re.S)
        if not match:
            continue
        games = []
        for row in re.findall(r"<tr[^>]*>(.*?)</tr>", match.group(0), flags=re.S):
            value = cell(row, "games").replace(",", "")
            if value.isdigit():
                games.append(int(value))
        if not games or max(games) > 38:
            continue
        if best is None or len(games) > best[0]:
            best = (len(games), match.group(0))
    return None if best is None else best[1]


def parse_squad_players(html):
    table = league_player_table(html)
    if not table:
        return []
    players = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, flags=re.S):
        link = re.search(r'href="(?:https://fbref.com)?(/en/players/([^/]+)/[^"]+)"[^>]*>([^<]+)', row)
        if not link:
            continue
        starts = cell(row, "games_starts").replace(",", "")
        apps = cell(row, "games").replace(",", "")
        if not starts.isdigit() or not apps.isdigit():
            continue
        players.append({
            "fbref_id": link.group(2),
            "player": strip_tags(link.group(3)),
            "starts": int(starts),
            "appearances": int(apps),
        })
    return players


def squad_candidates(squad_url):
    match = re.search(r"/en/squads/([a-z0-9]+)/(\d{4}-\d{4})/([^/]+)$", squad_url)
    if not match:
        return [squad_url]
    squad_id, season, slug = match.groups()
    name = slug[:-6] if slug.endswith("-Stats") else slug
    league_specific = f"https://fbref.com/en/squads/{squad_id}/{season}/c9/{name}-Stats-Premier-League"
    return [league_specific, squad_url]


def squad_links(html, label):
    found = sorted(set(re.findall(rf'/en/squads/[a-z0-9]+/{label}/[^"#]+', html)))
    return ["https://fbref.com" + path for path in found if path.endswith("-Stats") or "Stats" in path]


def save_fbref(end_years):
    pages = RAW / "fbref"
    pages.mkdir(parents=True, exist_ok=True)
    tables = []
    players = []
    for end_year in end_years:
        label = season_label(end_year)
        original = f"https://fbref.com/en/comps/9/{label}/{label}-Premier-League-Stats"
        main_path = pages / f"{end_year}.html"
        if not main_path.exists():
            text, timestamp, used = download_archived([original])
            main_path.write_text(text, encoding="utf-8")
            (pages / f"{end_year}.timestamp").write_text(timestamp + "\n" + used + "\n", encoding="utf-8")
            print("fbref", end_year, timestamp, flush=True)
            pause()
        html = main_path.read_text(encoding="utf-8", errors="replace")
        table = parse_league_table(html)
        if len(table) < 20 or any(row["games"] != 38 for row in table):
            raise SystemExit(f"Season {label} table is not a complete 38-game table ({len(table)} clubs)")
        for row in table:
            tables.append({"season_end": end_year, **row})
        for squad_url in squad_links(html, label):
            slug = squad_url.rstrip("/").split("/")[-1]
            squad_path = pages / f"{end_year}-{slug}.html"
            if not squad_path.exists():
                text, _timestamp, _used = download_archived(squad_candidates(squad_url))
                squad_path.write_text(text, encoding="utf-8")
                print("squad", end_year, slug, flush=True)
                pause()
            squad_html = squad_path.read_text(encoding="utf-8", errors="replace")
            club = slug.replace("-Stats", "").replace("-", " ")
            parsed = parse_squad_players(squad_html)
            if not parsed:
                raise SystemExit(f"No Premier League player table in {squad_path.name}")
            for player in parsed:
                players.append({"season_end": end_year, "fbref_club": club, **player})
    write_csv(RAW / "fbref-table.csv", tables, ["season_end", "team", "points", "games"])
    write_csv(RAW / "fbref-players.csv", players, ["season_end", "fbref_club", "player", "fbref_id", "starts", "appearances"])


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def parse_tm_clubs(page):
    clubs = []
    seen = set()
    for href, club_id, name in re.findall(
        r'href="(/[^"]+/startseite/verein/(\d+)[^"]*)"[^>]*>([^<]+)',
        page,
    ):
        club_id = href.split("/verein/")[1].split("/")[0]
        club_name = html.unescape(re.sub(r"\s+", " ", name).strip())
        if not club_name or club_id in seen or club_name.lower() in {"premier league"}:
            continue
        seen.add(club_id)
        clubs.append({"tm_club_id": club_id, "tm_club": club_name})
    return clubs


def parse_tm_squad(page):
    players = []
    seen = set()
    for _href, player_id, name in re.findall(r'href="(/[^"]+/profil/spieler/(\d+))"[^>]*>([^<]+)', page):
        if player_id in seen:
            continue
        seen.add(player_id)
        players.append({"tm_id": player_id, "player": html.unescape(re.sub(r"\s+", " ", name).strip())})
    title = re.search(r"<title>([^<]+)", page)
    club = html.unescape(title.group(1).split(" - ")[0].strip()) if title else ""
    return club, players


def save_transfermarkt(end_years):
    pages = RAW / "tm"
    pages.mkdir(parents=True, exist_ok=True)
    squads = []
    for end_year in end_years:
        start = end_year - 1
        league_path = pages / f"league-{start}.html"
        if not league_path.exists():
            url = f"https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1/plus/?saison_id={start}"
            league_path.write_text(fetch_text(url), encoding="utf-8")
            print("tm league", start, flush=True)
            pause()
        clubs = parse_tm_clubs(league_path.read_text(encoding="utf-8", errors="replace"))
        if len(clubs) < 20:
            raise SystemExit(f"Transfermarkt league page {start} has {len(clubs)} clubs")
        for club in clubs:
            squad_path = pages / f"squad-{club['tm_club_id']}-{start}.html"
            if not squad_path.exists():
                url = (
                    "https://www.transfermarkt.com/kader/kader/verein/"
                    f"{club['tm_club_id']}/saison_id/{start}"
                )
                squad_path.write_text(fetch_text(url), encoding="utf-8")
                print("tm squad", start, club["tm_club"], flush=True)
                pause()
            club_name, players = parse_tm_squad(squad_path.read_text(encoding="utf-8", errors="replace"))
            if len(players) < 10:
                raise SystemExit(f"Short squad {club_name} {start}: {len(players)}")
            for player in players:
                squads.append({
                    "season_end": end_year,
                    "tm_club_id": club["tm_club_id"],
                    "tm_club": club_name or club["tm_club"],
                    **player,
                })
    write_csv(RAW / "tm-squads.csv", squads, ["season_end", "tm_club_id", "tm_club", "tm_id", "player"])


def save_transfer_history(player_ids):
    dest_dir = RAW / "transfers"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for player_id in player_ids:
        dest = dest_dir / f"{player_id}.json"
        if dest.exists() and dest.stat().st_size > 20:
            continue
        url = f"https://www.transfermarkt.com/ceapi/transferHistory/list/{player_id}"
        dest.write_bytes(fetch(url))
        print("transfer", player_id, flush=True)
        pause()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--transfers":
        player_ids = Path(sys.argv[2]).read_text(encoding="utf-8").split()
        save_transfer_history(player_ids)
        return
    end_years = list(range(1996, 2027))
    if len(sys.argv) > 1 and sys.argv[1] == "--years":
        end_years = [int(value) for value in sys.argv[2].split(",")]
    RAW.mkdir(parents=True, exist_ok=True)
    save_matches(end_years)
    save_fbref(end_years)
    save_transfermarkt(end_years)


if __name__ == "__main__":
    main()

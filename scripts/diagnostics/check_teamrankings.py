#!/usr/bin/env python3
"""One-off diagnostic: check which TeamRankings projections/standings pages
exist and whether they have a title-probability column (e.g. "Win SB").

Not part of the daily pipeline - run manually via the check-teamrankings
workflow to confirm URLs/table structure before building the real scraper
provider. Prints headers + a couple of sample rows per candidate URL.
"""
import sys
import time

import requests
from bs4 import BeautifulSoup

USER_AGENT = "FuturesValueTracker/1.0 (+https://github.com/niksmdmarketing/futures-value-tracker; one daily request per competition)"

CANDIDATE_URLS = [
    "https://www.teamrankings.com/nfl/projections/standings/",
    "https://www.teamrankings.com/nba/projections/standings/",
    "https://www.teamrankings.com/mlb/projections/standings/",
    "https://www.teamrankings.com/nhl/projections/standings/",
    "https://www.teamrankings.com/college-football/projections/standings/",
    "https://www.teamrankings.com/ncaa-football/projections/standings/",
    "https://www.teamrankings.com/college-basketball/projections/standings/",
    "https://www.teamrankings.com/ncaa-basketball/projections/standings/",
]


def check_robots():
    resp = requests.get(
        "https://www.teamrankings.com/robots.txt",
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    print("=== robots.txt (status %s) ===" % resp.status_code)
    print(resp.text)
    print()


def check_url(url: str):
    print(f"=== {url} ===")
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    except requests.RequestException as exc:
        print(f"  request failed: {exc}")
        return
    print(f"  status: {resp.status_code}")
    if resp.status_code != 200:
        return

    soup = BeautifulSoup(resp.text, "lxml")
    tables = soup.find_all("table")
    print(f"  tables found: {len(tables)}")
    for i, table in enumerate(tables):
        header_row = table.find("tr")
        if header_row is None:
            continue
        headers = [c.get_text(strip=True) for c in header_row.find_all(["th", "td"])]
        print(f"  table[{i}] headers: {headers}")
        body_rows = table.find_all("tr")[1:4]
        for row in body_rows:
            cells = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
            print(f"    sample row: {cells}")
    print()


def main():
    check_robots()
    for url in CANDIDATE_URLS:
        check_url(url)
        time.sleep(2)


if __name__ == "__main__":
    sys.exit(main())

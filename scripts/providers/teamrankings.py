"""Provider that scrapes team title-win probabilities from TeamRankings
projections/standings pages (e.g. nfl/projections/standings/).

Each page renders one <table> per division/conference. Within a table,
a "header" row (team-name-ish label in cell 0, then W/L/T-style column
names) precedes a block of team rows sharing that column layout, and this
pattern repeats for every division/conference on the page. So the column
index for the target metric (e.g. "Win SB") is looked up fresh from each
header row rather than assumed fixed.

Respects the site's robots.txt Crawl-delay (10s) between requests.
"""
import time

import requests
from bs4 import BeautifulSoup

from .probability_base import ProbabilityProvider, TeamProbability

USER_AGENT = (
    "FuturesValueTracker/1.0 "
    "(+https://github.com/niksmdmarketing/futures-value-tracker; "
    "one daily request per competition)"
)
CRAWL_DELAY_SECONDS = 10.0

# Marks the start of a division/conference's header row: its second cell
# (after the team/division name) is always one of these column labels.
_HEADER_MARKERS = {"W", "L", "T", "overall W", "conf W"}


def _parse_percent(text: str) -> float | None:
    text = text.strip()
    if not text or text == "--":
        return None
    if text.endswith("%"):
        text = text[:-1]
    try:
        return float(text) / 100.0
    except ValueError:
        return None


class TeamRankingsProvider(ProbabilityProvider):
    name = "teamrankings"

    def __init__(self) -> None:
        self._last_request_at: float | None = None

    def fetch_probabilities(self, source: dict) -> list[TeamProbability]:
        url = source["url"]
        target_column = source["column"]

        self._respect_crawl_delay()
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        results: list[TeamProbability] = []

        for table in soup.find_all("table"):
            current_col: int | None = None
            for tr in table.find_all("tr"):
                cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
                if len(cells) < 2:
                    continue
                if cells[1] in _HEADER_MARKERS:
                    current_col = cells.index(target_column) if target_column in cells else None
                    continue
                if current_col is None or current_col >= len(cells):
                    continue
                team = cells[0]
                if not team:
                    continue
                probability = _parse_percent(cells[current_col])
                if probability is None:
                    continue
                results.append({"team": team, "probability": probability})

        return results

    def _respect_crawl_delay(self) -> None:
        if self._last_request_at is not None:
            elapsed = time.monotonic() - self._last_request_at
            remaining = CRAWL_DELAY_SECONDS - elapsed
            if remaining > 0:
                time.sleep(remaining)
        self._last_request_at = time.monotonic()

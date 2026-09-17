#!/usr/bin/env python3
"""One-off: for each tracked competition, print the full team-name list
from TeamRankings (model side) and from The Odds API / bookmakers (odds
side), so the team_mapping.py lookup table can be built from real values
instead of guesses. Not part of the daily pipeline.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import COMPETITIONS
from providers.odds_api import TheOddsApiProvider
from providers.teamrankings import TeamRankingsProvider


def main() -> None:
    odds_provider = TheOddsApiProvider()
    prob_provider = TeamRankingsProvider()

    for competition in COMPETITIONS:
        sport_key = competition["key"]
        print(f"\n===== {sport_key} =====")

        teams = prob_provider.fetch_probabilities(competition["probability_source"])
        tr_names = sorted(t["team"] for t in teams)
        print(f"TeamRankings ({len(tr_names)}): {tr_names}")

        payload = odds_provider.fetch_outrights(sport_key)
        odds_names = set()
        for event in payload:
            for bm in event.get("bookmakers", []):
                for market in bm.get("markets", []):
                    for outcome in market.get("outcomes", []):
                        odds_names.add(outcome["name"])
        print(f"OddsAPI ({len(odds_names)}): {sorted(odds_names)}")


if __name__ == "__main__":
    main()

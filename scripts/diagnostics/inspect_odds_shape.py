#!/usr/bin/env python3
"""One-off: fetch a single competition's outrights and print its JSON
shape (structure + a couple of sample outcomes per bookmaker), to design
the calculation/matching script against the real payload rather than
guessing. Not part of the daily pipeline.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from providers.odds_api import TheOddsApiProvider


def main() -> None:
    provider = TheOddsApiProvider()
    payload = provider.fetch_outrights("americanfootball_nfl_super_bowl_winner")

    print(f"Top-level type: {type(payload).__name__}, length: {len(payload)}")
    for event in payload:
        print("--- event ---")
        print("keys:", list(event.keys()))
        for k in ("id", "sport_key", "sport_title", "commence_time", "home_team", "away_team"):
            print(f"  {k}: {event.get(k)!r}")
        bookmakers = event.get("bookmakers", [])
        print(f"  bookmakers: {len(bookmakers)}")
        for bm in bookmakers:
            print(f"  --- bookmaker: {bm.get('key')} ({bm.get('title')}) last_update={bm.get('last_update')} ---")
            print("    bookmaker keys:", list(bm.keys()))
            for market in bm.get("markets", []):
                print(f"    market key={market.get('key')} last_update={market.get('last_update')}")
                print("    market keys:", list(market.keys()))
                outcomes = market.get("outcomes", [])
                print(f"    outcomes: {len(outcomes)}")
                for o in outcomes[:5]:
                    print("      sample outcome:", json.dumps(o))


if __name__ == "__main__":
    main()

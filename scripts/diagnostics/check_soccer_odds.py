#!/usr/bin/env python3
"""One-off: check whether The Odds API currently offers outrights for
any soccer league (EPL, Champions League, A-League, etc). Listing sports
costs no credits. Not part of the daily pipeline.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from providers.odds_api import TheOddsApiProvider


def main():
    provider = TheOddsApiProvider()
    sports = provider.list_sports()
    soccer = [s for s in sports if s["key"].startswith("soccer")]
    print(f"{len(soccer)} soccer entries in sports list")
    for s in soccer:
        print(f"  key={s['key']!r} active={s['active']} has_outrights={s.get('has_outrights')} title={s['title']!r}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""One-off: fetch The Odds API's own marketing/pricing pages to check
whether soccer outrights coverage is plan-dependent (a higher tier might
unlock them) before looking at third-party providers. Not part of the
daily pipeline.
"""
import re

import requests

USER_AGENT = "FuturesValueTracker/1.0 (+https://github.com/niksmdmarketing/futures-value-tracker)"

PAGES = [
    "https://the-odds-api.com/",
    "https://the-odds-api.com/sports-odds-data/soccer-odds.html",
    "https://the-odds-api.com/sports-odds-data/epl-odds.html",
]


def main():
    for url in PAGES:
        print(f"\n=== {url} ===")
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
            print(f"status: {resp.status_code}, length: {len(resp.text)}")
            text = re.sub(r"<[^>]+>", " ", resp.text)
            text = re.sub(r"\s+", " ", text).strip()
            # Print anything mentioning outright/future/plan/tier
            for keyword in ["outright", "future", "plan", "tier", "500 requests", "20,000", "per month"]:
                idxs = [m.start() for m in re.finditer(re.escape(keyword), text, re.I)]
                for idx in idxs[:5]:
                    snippet = text[max(0, idx - 100):idx + 150]
                    print(f"  [{keyword}] ...{snippet}...")
        except requests.RequestException as exc:
            print(f"request failed: {exc}")


if __name__ == "__main__":
    main()

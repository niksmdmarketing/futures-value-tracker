#!/usr/bin/env python3
"""One-off: check robots.txt for Sportsbet and TAB before considering
whether scraping either is viable/permitted. Not part of the daily
pipeline.
"""
import requests

USER_AGENT = "FuturesValueTracker/1.0 (+https://github.com/niksmdmarketing/futures-value-tracker)"

SITES = [
    "https://www.sportsbet.com.au",
    "https://www.tab.com.au",
]


def main():
    for base in SITES:
        print(f"\n=== {base}/robots.txt ===")
        try:
            resp = requests.get(f"{base}/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=20)
            print(f"status: {resp.status_code}")
            print(resp.text[:4000])
        except requests.RequestException as exc:
            print(f"request failed: {exc}")

        print(f"\n=== {base}/ (homepage, plain HTTP) ===")
        try:
            resp = requests.get(base + "/", headers={"User-Agent": USER_AGENT}, timeout=20, allow_redirects=True)
            print(f"status: {resp.status_code}, final_url: {resp.url}, length: {len(resp.text)}")
        except requests.RequestException as exc:
            print(f"request failed: {exc}")


if __name__ == "__main__":
    main()

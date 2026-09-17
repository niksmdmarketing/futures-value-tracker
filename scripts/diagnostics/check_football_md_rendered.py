#!/usr/bin/env python3
"""One-off: use a real browser to render football-md.com's /terms page
(and take a look at /login) since the site is a client-side-rendered SPA
that a plain HTTP fetch can't see into. Checks specifically for language
about automated access / scraping / bots / API use. Not part of the
daily pipeline.
"""
import re

from playwright.sync_api import sync_playwright

KEYWORDS = re.compile(
    r"automat|scrap|bot|crawl|robot|api\b|rate limit|throttl|reverse engineer|"
    r"unauthorized access|circumvent",
    re.I,
)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for path in ["/terms", "/login"]:
            url = f"https://football-md.com{path}"
            print(f"\n=== {url} ===")
            try:
                page.goto(url, wait_until="networkidle", timeout=20000)
                page.wait_for_timeout(1000)
                text = page.inner_text("body")
                print(f"rendered text length: {len(text)} chars")

                hits = []
                for line in text.split("\n"):
                    line = line.strip()
                    if line and KEYWORDS.search(line):
                        hits.append(line)
                if hits:
                    print("Lines mentioning automation/scraping/bots/API/rate-limits:")
                    for h in hits[:20]:
                        print("  -", h[:300])
                else:
                    print("No lines matched automation/scraping/bot/API keywords.")

                print("--- first 1000 chars of rendered text ---")
                print(text[:1000])
            except Exception as exc:  # noqa: BLE001
                print(f"failed to load: {exc}")

        browser.close()


if __name__ == "__main__":
    main()

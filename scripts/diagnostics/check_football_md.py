#!/usr/bin/env python3
"""One-off: check football-md.com's robots.txt and homepage/terms links
before deciding whether/how to automate fetching from it. Not part of the
daily pipeline.
"""
import re

import requests

USER_AGENT = "FuturesValueTracker/1.0 (+https://github.com/niksmdmarketing/futures-value-tracker)"


def main():
    print("=== robots.txt ===")
    try:
        resp = requests.get("https://football-md.com/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=30)
        print(f"status: {resp.status_code}")
        print(resp.text)
    except requests.RequestException as exc:
        print(f"request failed: {exc}")

    print("\n=== homepage ===")
    try:
        resp = requests.get("https://football-md.com/", headers={"User-Agent": USER_AGENT}, timeout=30)
        print(f"status: {resp.status_code}")
        print(f"final url: {resp.url}")
        html = resp.text
        print(f"length: {len(html)} chars")

        # Look for links that might be terms/privacy/login pages.
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        interesting = [
            l for l in links
            if re.search(r"term|privacy|acceptable|policy|login|sign-?in|api|pricing", l, re.I)
        ]
        print("Interesting links found:")
        for l in sorted(set(interesting)):
            print(" ", l)

        title_match = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
        if title_match:
            print("Title:", title_match.group(1).strip())
        print("--- first 1500 chars of homepage HTML ---")
        print(html[:1500])
    except requests.RequestException as exc:
        print(f"request failed: {exc}")

    print("\n=== common paths ===")
    for path in ["/terms", "/terms-of-service", "/tos", "/legal", "/privacy", "/login", "/pricing", "/about", "/api", "/docs", "/sitemap.xml"]:
        url = f"https://football-md.com{path}"
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15, allow_redirects=True)
            print(f"{path}: status={resp.status_code} final_url={resp.url} length={len(resp.text)}")
        except requests.RequestException as exc:
            print(f"{path}: request failed: {exc}")


if __name__ == "__main__":
    main()

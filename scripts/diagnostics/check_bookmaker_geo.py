#!/usr/bin/env python3
"""One-off: check whether sportsbet.com.au and tab.com.au are reachable
at all from this runner using a real headless browser (realistic Chrome
UA, full JS/TLS), and log any XHR/fetch network requests made during
page load (a lead on an internal JSON API). Not part of the daily
pipeline - this only answers "does it load", before any scraper is
built.
"""
from playwright.sync_api import sync_playwright

SITES = [
    ("sportsbet", "https://www.sportsbet.com.au/"),
    ("tab", "https://www.tab.com.au/"),
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for name, url in SITES:
            print(f"\n{'=' * 20} {name}: {url} {'=' * 20}")
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                ),
                locale="en-AU",
                timezone_id="Australia/Melbourne",
            )
            page = context.new_page()

            xhr_requests = []

            def on_request(req):
                if req.resource_type in ("xhr", "fetch"):
                    xhr_requests.append(f"{req.method} {req.url}")

            page.on("request", on_request)

            try:
                response = page.goto(url, wait_until="networkidle", timeout=30000)
                print(f"HTTP status: {response.status if response else 'no response'}")
                print(f"final URL: {page.url}")
                page.wait_for_timeout(2000)

                title = page.title()
                print(f"title: {title!r}")

                body_text = page.inner_text("body")
                print(f"body text length: {len(body_text)} chars")
                print("--- first 500 chars of visible body text ---")
                print(body_text[:500])

                lower = body_text.lower()
                for flag in ["not available", "restricted", "blocked", "captcha", "access denied", "verify you are human", "location"]:
                    if flag in lower:
                        print(f"  [flag] page text contains: {flag!r}")

                screenshot_path = f"/tmp/{name}_screenshot.png"
                page.screenshot(path=screenshot_path, full_page=False)
                print(f"screenshot saved: {screenshot_path}")

            except Exception as exc:  # noqa: BLE001
                print(f"FAILED TO LOAD: {exc}")

            print(f"\nXHR/fetch requests seen ({len(xhr_requests)}):")
            for r in xhr_requests[:40]:
                print(f"  {r}")

            context.close()

        browser.close()


if __name__ == "__main__":
    main()

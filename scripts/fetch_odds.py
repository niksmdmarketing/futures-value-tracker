#!/usr/bin/env python3
"""Fetch raw futures/outrights odds for the tracked competitions and save
them to data/raw/.

Behaviour:
- Checks the live sports list first (no credit cost) and skips any
  competition that is inactive or doesn't offer an outrights market.
- Fetches all remaining competitions into memory, and only writes to disk
  once every fetch has succeeded, so a failed/partial run never overwrites
  good data already on disk.
- Logs credit usage (x-requests-used / x-requests-remaining) after each
  call.
- Exits non-zero with a clear error message on any failure.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import COMPETITIONS
from providers.odds_api import TheOddsApiProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fetch_odds")

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"


def main() -> None:
    provider = TheOddsApiProvider()

    logger.info("Checking active sports/competitions (no credit cost)...")
    sports = provider.list_sports()
    by_key = {s["key"]: s for s in sports}

    to_fetch = []
    for competition in COMPETITIONS:
        sport_key = competition["key"]
        info = by_key.get(sport_key)
        if info is None:
            logger.warning("Competition %s not found in sports list, skipping", sport_key)
            continue
        if not info.get("active", False):
            logger.info("Competition %s is inactive, skipping", sport_key)
            continue
        if not info.get("has_outrights", False):
            logger.warning("Competition %s has no outrights market, skipping", sport_key)
            continue
        to_fetch.append(sport_key)

    if not to_fetch:
        raise RuntimeError("No active competitions with outrights markets to fetch")

    logger.info("Fetching outrights for: %s", ", ".join(to_fetch))

    results = {}
    for sport_key in to_fetch:
        logger.info("Fetching %s ...", sport_key)
        payload = provider.fetch_outrights(sport_key)
        logger.info(
            "  -> %d bookmaker entries. Credits used=%s remaining=%s",
            len(payload) if isinstance(payload, list) else 0,
            provider.last_headers.get("requests_used"),
            provider.last_headers.get("requests_remaining"),
        )
        results[sport_key] = payload

    # Every fetch succeeded - now, and only now, write to disk.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).isoformat()
    for sport_key, payload in results.items():
        out_path = DATA_DIR / f"{sport_key}.json"
        out_path.write_text(json.dumps(payload, indent=2))
        logger.info("Wrote %s", out_path)

    meta = {
        "fetched_at": fetched_at,
        "competitions": to_fetch,
        "provider": provider.name,
        "last_requests_used": provider.last_headers.get("requests_used"),
        "last_requests_remaining": provider.last_headers.get("requests_remaining"),
    }
    (DATA_DIR / "_meta.json").write_text(json.dumps(meta, indent=2))
    logger.info("Done. Credits remaining: %s", provider.last_headers.get("requests_remaining"))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - top-level script guard
        logger.error("Fetch failed: %s", exc)
        sys.exit(1)

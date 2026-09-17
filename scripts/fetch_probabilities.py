#!/usr/bin/env python3
"""Fetch model title-win probabilities for the tracked competitions and
save them to data/raw/probabilities/.

Mirrors fetch_odds.py's safety pattern: fetches every competition into
memory first, and only writes to disk once all of them have succeeded, so
a failed/partial run never overwrites good data already on disk.

Validates that each competition's probabilities sum to roughly 100% (a
sanity check on the source data) and logs a warning if not.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import COMPETITIONS
from providers.csv_probabilities import CsvProbabilityProvider
from providers.teamrankings import TeamRankingsProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("fetch_probabilities")

DATA_DIR = Path(__file__).parent.parent / "data" / "raw" / "probabilities"

PROVIDERS = {
    "teamrankings": TeamRankingsProvider(),
    "csv": CsvProbabilityProvider(),
}

SUM_TOLERANCE = 0.05  # flag if a competition's probabilities sum outside 95-105%
DOMINANT_TEAM_THRESHOLD = 0.5  # flag if one team alone exceeds this share


def main() -> None:
    results = {}
    for competition in COMPETITIONS:
        sport_key = competition["key"]
        source = competition["probability_source"]
        provider = PROVIDERS.get(source["provider"])
        if provider is None:
            raise RuntimeError(f"Unknown probability provider '{source['provider']}' for {sport_key}")

        logger.info("Fetching probabilities for %s via %s (%s)...", sport_key, provider.name, source.get("url", source.get("path")))
        teams = provider.fetch_probabilities(source)
        if not teams:
            raise RuntimeError(f"No probabilities parsed for {sport_key}")

        total = sum(t["probability"] for t in teams)
        logger.info("  -> %d teams, probabilities sum to %.1f%%", len(teams), total * 100)
        if abs(total - 1.0) > SUM_TOLERANCE:
            logger.warning(
                "  Probabilities for %s sum to %.1f%%, expected ~100%%",
                sport_key,
                total * 100,
            )

        # A sum that adds up to ~100% can still hide bad source data: e.g.
        # one team showing 100% and everyone else 0%, which happens on
        # TeamRankings pages before a season's title odds are really
        # computed. No real multi-team title race has one team this far
        # ahead of the field, so flag it as suspect for calculate.py to
        # skip rather than publish a nonsense edge.
        suspect = False
        if len(teams) > 5:
            favourite = max(teams, key=lambda t: t["probability"])
            if favourite["probability"] > DOMINANT_TEAM_THRESHOLD:
                suspect = True
                logger.error(
                    "  '%s' at %.1f%% dominates %s (%d teams) - implausible this far out, "
                    "flagging as suspect",
                    favourite["team"],
                    favourite["probability"] * 100,
                    sport_key,
                    len(teams),
                )

        results[sport_key] = {
            "competition_name": competition["name"],
            "teams": teams,
            "probability_sum": total,
            "suspect": suspect,
        }

    # Every fetch succeeded - now, and only now, write to disk.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fetched_at = datetime.now(timezone.utc).isoformat()
    for sport_key, payload in results.items():
        out_path = DATA_DIR / f"{sport_key}.json"
        out_path.write_text(json.dumps(payload, indent=2))
        logger.info("Wrote %s", out_path)

    meta = {
        "fetched_at": fetched_at,
        "competitions": list(results.keys()),
    }
    (DATA_DIR / "_meta.json").write_text(json.dumps(meta, indent=2))
    logger.info("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - top-level script guard
        logger.error("Fetch failed: %s", exc)
        sys.exit(1)

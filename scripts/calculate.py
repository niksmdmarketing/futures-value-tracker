#!/usr/bin/env python3
"""Combine fetched odds + model probabilities into the ranked edge data
the static site reads (docs/data.json).

Reads data/raw/<sport_key>.json (odds) and
data/raw/probabilities/<sport_key>.json (probabilities), both written by
fetch_odds.py / fetch_probabilities.py. Computes, per team:
- fair odds = 1 / model probability
- best available price across Sportsbet/TAB/Unibet
- edge (expected value) = model probability x best price - 1
- an annualised edge, using the competition's commence_time, since futures
  money is tied up until the event resolves

Also computes each bookmaker's market overround (sum of 1/price across all
its outcomes) per competition, and re-checks each competition's model
probabilities sum to ~100%.

Any team in the probabilities that can't be mapped to an odds-side name
(scripts/team_mapping.py), or has no bookmaker price that day, is logged
and excluded from the ranked output rather than silently dropped.

Like the fetch scripts, computes everything in memory and only writes
docs/data.json once fully successful, preserving the previous good file on
any failure.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))

from config import COMPETITIONS
from team_mapping import map_team_name

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("calculate")

RAW_ODDS_DIR = Path(__file__).parent.parent / "data" / "raw"
RAW_PROB_DIR = Path(__file__).parent.parent / "data" / "raw" / "probabilities"
OUTPUT_PATH = Path(__file__).parent.parent / "docs" / "data.json"

MELBOURNE_TZ = ZoneInfo("Australia/Melbourne")
BOOKMAKERS = ["sportsbet", "tab", "unibet"]
PROBABILITY_SUM_TOLERANCE = 0.05


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")
    return json.loads(path.read_text())


def _index_odds(payload: list) -> tuple[dict[str, dict[str, float]], dict[str, str], dict[str, float]]:
    """Return (prices[team][bookmaker] -> price, last_update[bookmaker], overround[bookmaker])."""
    prices: dict[str, dict[str, float]] = {}
    last_update: dict[str, str] = {}
    overround: dict[str, float] = {}

    for event in payload:
        for bm in event.get("bookmakers", []):
            bm_key = bm["key"]
            last_update[bm_key] = bm.get("last_update")
            for market in bm.get("markets", []):
                if market.get("key") != "outrights":
                    continue
                implied_sum = 0.0
                for outcome in market.get("outcomes", []):
                    name = outcome["name"]
                    price = outcome["price"]
                    implied_sum += 1.0 / price
                    prices.setdefault(name, {})[bm_key] = price
                overround[bm_key] = implied_sum

    return prices, last_update, overround


def _days_until(commence_time: str | None, now: datetime) -> float | None:
    if not commence_time:
        return None
    try:
        event_dt = datetime.fromisoformat(commence_time.replace("Z", "+00:00"))
    except ValueError:
        return None
    days = (event_dt - now).total_seconds() / 86400
    return days if days > 0 else None


def main() -> None:
    now = datetime.now(timezone.utc)
    all_teams = []
    competition_meta = []
    unmatched = []

    for competition in COMPETITIONS:
        sport_key = competition["key"]
        name = competition["name"]

        odds_payload = _load_json(RAW_ODDS_DIR / f"{sport_key}.json")
        prob_payload = _load_json(RAW_PROB_DIR / f"{sport_key}.json")

        prices_by_team, last_update_by_bm, overround_by_bm = _index_odds(odds_payload)

        commence_time = odds_payload[0].get("commence_time") if odds_payload else None
        days_to_event = _days_until(commence_time, now)

        prob_sum = prob_payload.get("probability_sum")
        if prob_sum is not None and abs(prob_sum - 1.0) > PROBABILITY_SUM_TOLERANCE:
            logger.warning(
                "%s: model probabilities sum to %.1f%%, expected ~100%%",
                sport_key,
                prob_sum * 100,
            )

        for team_prob in prob_payload["teams"]:
            model_team = team_prob["team"]
            probability = team_prob["probability"]

            odds_team = map_team_name(sport_key, model_team)
            if odds_team is None:
                logger.warning("%s: no team-name mapping for '%s' - skipping", sport_key, model_team)
                unmatched.append({"competition_key": sport_key, "team": model_team, "reason": "no_mapping"})
                continue

            team_prices = prices_by_team.get(odds_team)
            if not team_prices:
                logger.warning(
                    "%s: '%s' (%s) has no bookmaker price today - skipping",
                    sport_key,
                    model_team,
                    odds_team,
                )
                unmatched.append({"competition_key": sport_key, "team": model_team, "reason": "no_odds_today"})
                continue

            best_bookmaker = max(team_prices, key=team_prices.get)
            best_price = team_prices[best_bookmaker]
            fair_odds = 1.0 / probability if probability > 0 else None
            edge = probability * best_price - 1.0

            annualised_edge = None
            if days_to_event:
                annualised_edge = (1.0 + edge) ** (365.0 / days_to_event) - 1.0

            all_teams.append(
                {
                    "competition_key": sport_key,
                    "competition_name": name,
                    "team": odds_team,
                    "model_probability": probability,
                    "fair_odds": fair_odds,
                    "prices": {bm: team_prices.get(bm) for bm in BOOKMAKERS},
                    "best_price": best_price,
                    "best_bookmaker": best_bookmaker,
                    "edge": edge,
                    "annualised_edge": annualised_edge,
                }
            )

        competition_meta.append(
            {
                "key": sport_key,
                "name": name,
                "commence_time": commence_time,
                "days_to_event": days_to_event,
                "bookmaker_overround": overround_by_bm,
                "bookmaker_last_update": last_update_by_bm,
                "probability_sum": prob_sum,
            }
        )

    if not all_teams:
        raise RuntimeError("No teams produced a matched edge - refusing to write an empty data.json")

    all_teams.sort(key=lambda t: t["edge"], reverse=True)

    output = {
        "generated_at": now.isoformat(),
        "generated_at_melbourne": now.astimezone(MELBOURNE_TZ).isoformat(),
        "competitions": competition_meta,
        "teams": all_teams,
        "unmatched": unmatched,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2))
    logger.info(
        "Wrote %s: %d teams, %d unmatched, top edge %.1f%%",
        OUTPUT_PATH,
        len(all_teams),
        len(unmatched),
        all_teams[0]["edge"] * 100,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - top-level script guard
        logger.error("Calculation failed: %s", exc)
        sys.exit(1)

"""Provider for The Odds API (https://the-odds-api.com), v4."""
import os
from typing import Any

import requests

from .base import OddsProvider

API_BASE = "https://api.the-odds-api.com/v4"


class TheOddsApiProvider(OddsProvider):
    name = "the-odds-api"

    def __init__(self, api_key: str | None = None, regions: str = "au", odds_format: str = "decimal"):
        self.api_key = api_key or os.environ.get("ODDS_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "ODDS_API_KEY is not set. Set it as an environment variable "
                "(locally) or a GitHub Actions secret (in CI)."
            )
        self.regions = regions
        self.odds_format = odds_format
        self.last_headers: dict[str, str | None] = {}

    def list_sports(self) -> list[dict[str, Any]]:
        resp = requests.get(
            f"{API_BASE}/sports/",
            params={"all": "true", "apiKey": self.api_key},
            timeout=30,
        )
        resp.raise_for_status()
        self._record_usage(resp)
        return resp.json()

    def fetch_outrights(self, sport_key: str) -> Any:
        resp = requests.get(
            f"{API_BASE}/sports/{sport_key}/odds/",
            params={
                "regions": self.regions,
                "markets": "outrights",
                "oddsFormat": self.odds_format,
                "apiKey": self.api_key,
            },
            timeout=30,
        )
        resp.raise_for_status()
        self._record_usage(resp)
        return resp.json()

    def _record_usage(self, resp: requests.Response) -> None:
        self.last_headers = {
            "requests_used": resp.headers.get("x-requests-used"),
            "requests_remaining": resp.headers.get("x-requests-remaining"),
        }

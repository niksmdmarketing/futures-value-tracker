"""Abstract interface for a futures/outrights odds data source.

New data sources (e.g. a soccer-specific provider) implement this
interface and get picked up by the fetch script without changes to
the rest of the pipeline.
"""
from abc import ABC, abstractmethod
from typing import Any


class OddsProvider(ABC):
    name: str

    @abstractmethod
    def list_sports(self) -> list[dict[str, Any]]:
        """Return available sports/competitions, including 'active' and
        'has_outrights' flags, so callers can skip inactive ones."""

    @abstractmethod
    def fetch_outrights(self, sport_key: str) -> Any:
        """Return the raw outrights odds payload for one sport/competition."""

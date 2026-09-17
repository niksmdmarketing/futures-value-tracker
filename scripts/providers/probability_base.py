"""Abstract interface for a model-probability data source.

Each provider returns title-win probabilities for the teams in one
competition, in a normalized shape, so the calculation step doesn't care
whether the numbers came from scraping a site, a CSV file, or something
else added later.
"""
from abc import ABC, abstractmethod
from typing import TypedDict


class TeamProbability(TypedDict):
    team: str
    probability: float  # 0.0-1.0


class ProbabilityProvider(ABC):
    name: str

    @abstractmethod
    def fetch_probabilities(self, source: dict) -> list[TeamProbability]:
        """Return [{'team': ..., 'probability': ...}, ...] for one
        competition, given that competition's `probability_source` config
        dict (see scripts/config.py)."""

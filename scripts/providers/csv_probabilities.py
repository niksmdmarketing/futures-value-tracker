"""CSV-based probability provider, for competitions with no live source.

Not currently wired into any competition (see scripts/config.py) - NHL and
NCAAF were dropped rather than given a CSV fallback, since no CSV exists
yet. To add one later, point a competition's `probability_source` at
{"provider": "csv", "path": "data/probabilities.csv", "competition": "<key>"}
and this reads matching rows from a CSV with columns
`competition,team,probability` (probability as either a 0-1 fraction or a
percentage string like "12.5%").
"""
import csv
from pathlib import Path

from .probability_base import ProbabilityProvider, TeamProbability


class CsvProbabilityProvider(ProbabilityProvider):
    name = "csv"

    def fetch_probabilities(self, source: dict) -> list[TeamProbability]:
        path = Path(source["path"])
        competition = source["competition"]
        if not path.exists():
            raise FileNotFoundError(f"Probabilities CSV not found: {path}")

        results: list[TeamProbability] = []
        with path.open(newline="") as f:
            for row in csv.DictReader(f):
                if row["competition"] != competition:
                    continue
                prob_str = row["probability"].strip()
                probability = float(prob_str[:-1]) / 100.0 if prob_str.endswith("%") else float(prob_str)
                results.append({"team": row["team"].strip(), "probability": probability})
        return results

# Futures Value Tracker

Compares a betting model's probabilities against Australian bookmaker
futures (outright) odds, finds where a bookmaker's price is better than the
model's fair price, and publishes a ranked table of the biggest edges.

Futures/outright markets only (e.g. "NFL Super Bowl winner") — no
single-match markets.

## Status

This project is being built incrementally. Current state:

- [x] Repo scaffold
- [x] Odds fetch script (The Odds API)
- [x] Model probabilities fetch script (TeamRankings scraper)
- [ ] Calculations + team name matching
- [ ] Static site
- [ ] Daily automation + hosting

## Odds source

[The Odds API](https://the-odds-api.com/) v4, on a 500-credit/month plan.

- Listing sports costs no credits: `GET /v4/sports/?all=true`
- Futures odds cost 1 credit per call (1 region × 1 market):
  `GET /v4/sports/{sport_key}/odds/?regions=au&markets=outrights&oddsFormat=decimal`
- `regions=au` returns Sportsbet, TAB and Unibet in a single call.

Tracked competitions and their odds + probability sources are listed in
`scripts/config.py`. The odds fetch script checks each one against the live
`active` / `has_outrights` flags first (free) and skips anything inactive,
so an off-season competition never costs a credit.

### Tracked competitions

Currently: NFL Super Bowl, NBA Championship, MLB World Series.

NCAAF, NCAAB and NHL are deliberately left out for now — see the comment at
the top of `scripts/config.py` for why (in short: no reliable national-title
probability source exists yet for any of them; NCAAF and NCAAB's brackets
aren't set this far from their postseasons, and TeamRankings' NHL
projections page currently has no table at all). At 3 credits/run, a daily
run costs about 90 credits/month.

### Providers

Both odds and probabilities go through small provider abstractions, so
another data source (e.g. for soccer leagues, which The Odds API doesn't
cover for outrights) can be added later without reworking the rest of the
pipeline:

- Odds: `scripts/providers/base.py` (`OddsProvider`). The Odds API
  implementation is `scripts/providers/odds_api.py`.
- Probabilities: `scripts/providers/probability_base.py`
  (`ProbabilityProvider`). Implementations: `scripts/providers/teamrankings.py`
  (scrapes TeamRankings projections/standings pages, respecting its
  `Crawl-delay: 10` robots.txt directive) and `scripts/providers/csv_probabilities.py`
  (reads a `competition,team,probability` CSV — not wired up to any
  competition yet, ready for when one is needed).

## Configuration

The odds script reads its API key from the `ODDS_API_KEY` environment
variable — it is never hardcoded or committed. In GitHub Actions it comes
from the repository secret of the same name (already configured on this
repo). To run locally:

```bash
export ODDS_API_KEY=your-key-here
pip install -r requirements.txt
python scripts/fetch_odds.py
python scripts/fetch_probabilities.py
```

`fetch_odds.py` writes raw odds payloads to `data/raw/<sport_key>.json` plus
a `data/raw/_meta.json` with the fetch time and API credit usage.
`fetch_probabilities.py` writes `data/raw/probabilities/<sport_key>.json`
plus its own `_meta.json`, and logs a warning if a competition's
probabilities don't sum to roughly 100%. Both scripts only write to disk
once every competition has fetched successfully — a failed or partial run
leaves the previous good data untouched and exits non-zero.

## Automation

`.github/workflows/fetch-odds.yml` and `.github/workflows/fetch-probabilities.yml`
currently run on manual dispatch only (`workflow_dispatch`). A daily
schedule (~9am Melbourne time, handling the AEST/AEDT transition) and
GitHub Pages deploy are still to be built.

## Disclaimer

This project is analysis, not betting advice.

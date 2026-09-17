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
- [ ] Model probabilities input + calculations + team name matching
- [ ] Static site
- [ ] Daily automation + hosting

## Odds source

[The Odds API](https://the-odds-api.com/) v4, on a 500-credit/month plan.

- Listing sports costs no credits: `GET /v4/sports/?all=true`
- Futures odds cost 1 credit per call (1 region × 1 market):
  `GET /v4/sports/{sport_key}/odds/?regions=au&markets=outrights&oddsFormat=decimal`
- `regions=au` returns Sportsbet, TAB and Unibet in a single call.

Tracked competitions (The Odds API sport keys) are listed in
`scripts/config.py`. The fetch script checks each one against the live
`active` / `has_outrights` flags first (free) and skips anything inactive,
so an off-season competition never costs a credit. At ~6 credits/run, a
daily run costs about 180 credits/month.

### Providers

Odds fetching goes through a small provider abstraction
(`scripts/providers/base.py`), so another data source (e.g. for soccer
leagues, which The Odds API doesn't cover for outrights) can be added later
without reworking the rest of the pipeline. The Odds API implementation is
`scripts/providers/odds_api.py`.

## Configuration

The script reads the API key from the `ODDS_API_KEY` environment variable —
it is never hardcoded or committed. In GitHub Actions it comes from the
repository secret of the same name (already configured on this repo). To
run locally:

```bash
export ODDS_API_KEY=your-key-here
pip install -r requirements.txt
python scripts/fetch_odds.py
```

This writes raw odds payloads to `data/raw/<sport_key>.json` plus a
`data/raw/_meta.json` with the fetch time and API credit usage. A run only
writes to disk once every competition has fetched successfully — a failed
or partial run leaves the previous good data untouched and exits non-zero.

## Automation

`.github/workflows/fetch-odds.yml` currently runs on manual dispatch only
(`workflow_dispatch`). A daily schedule (~9am Melbourne time, handling the
AEST/AEDT transition) and GitHub Pages deploy will be added once the model
probabilities format is finalised.

## Disclaimer

This project is analysis, not betting advice.

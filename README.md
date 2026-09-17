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
- [x] Calculations + team name matching
- [x] Static site
- [x] Daily automation workflow (GitHub Pages hosting needs a one-time manual step — see below)

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

### Calculations and team-name matching

`scripts/team_mapping.py` is an explicit lookup table from each model
team name (TeamRankings) to its odds-side name (The Odds API /
bookmakers), built from real fetched data rather than guessed — see
`scripts/diagnostics/` history in git log for how it was derived. A team
with no entry is logged and excluded rather than silently dropped.

`scripts/calculate.py` combines the raw odds and probabilities into
`docs/data.json`, the file the site reads:

- fair odds = 1 / model probability
- best price across Sportsbet/TAB/Unibet, and the edge (expected value) =
  model probability × best price − 1
- an annualised edge using each competition's `commence_time`, since
  futures money is tied up until the event resolves
- each bookmaker's market overround (sum of 1/price across all its
  outcomes — futures books are often 120–140%)

It also re-checks the ~100% probability-sum validation, and skips a team
outright if its model probability rounds to 0.0% (TeamRankings' 1-decimal
precision — not a real zero, just noise that would otherwise show as a
meaningless "−100% edge"). More significantly, if one team holds more
than 50% of the probability across a field of 6+ teams, the whole
competition is flagged "suspect" and excluded — no real title race is
that lopsided this far out. This was needed in practice: TeamRankings'
NBA page briefly showed one team at 100% and the other 29 at 0%, which
would otherwise have produced a nonsense 1000%+ "edge".

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

## Site

`docs/index.html` + `docs/styles.css` + `docs/app.js` render `docs/data.json`
as a mobile-friendly table of teams ranked by edge, with filters for
sport, competition, bookmaker (recomputes edge off that bookmaker's own
price instead of the cross-shopped best price) and minimum edge; sortable
columns; positive edges highlighted; last-updated time in Melbourne time
plus each bookmaker's own `last_update`; per-competition market
overround; and an "unmatched teams" panel surfacing anything the
pipeline logged instead of silently dropping.

## Automation and hosting

`.github/workflows/update-site.yml` runs the full pipeline (fetch odds →
fetch probabilities → calculate edges) and commits the resulting
`docs/data.json` back to the repo, which is what keeps the live site
current. It only commits once every step has succeeded — a failure at any
point leaves the previously committed `docs/data.json` untouched and
fails the workflow run loudly.

It runs on `workflow_dispatch` (manual) and on a daily schedule aimed at
~4pm Melbourne time. Melbourne's UTC offset changes with daylight saving
(4pm AEST = 06:00 UTC; 4pm AEDT = 05:00 UTC), so rather than
hand-maintain the exact transition date every year, the workflow fires at
*both* possible UTC times daily and its first step checks the actual
current Melbourne hour (via the `Australia/Melbourne` IANA zone, which
already knows the real transition dates) — it skips the rest of the job
unless it's genuinely 4pm there. Exactly one of the two daily triggers
does the work, year-round, with no maintenance needed.

`.github/workflows/fetch-odds.yml` and `.github/workflows/fetch-probabilities.yml`
remain as standalone manual tools for debugging either half of the
pipeline in isolation.

**GitHub Pages setup (one-time, manual):** this repo's GitHub App
permissions don't extend to changing repository settings, so enabling
Pages itself needs a person with repo access: go to **Settings → Pages**
and set **Source: Deploy from a branch**, **Branch: `master` / `docs`**,
then save. After that, every successful `update-site` run publishes
automatically — no further manual steps.

## Disclaimer

This project is analysis, not betting advice.

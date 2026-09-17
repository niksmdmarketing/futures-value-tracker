"""Tracked competitions: odds source (The Odds API sport key) + model
probability source (TeamRankings projections page) for each.

Only competitions with BOTH an active outrights odds market AND a usable
title-probability source are tracked. fetch_odds.py double-checks each
sport key against the live Odds API sports list and skips anything
inactive, so no odds credits are wasted on an off-season competition.

americanfootball_ncaaf_championship_winner, basketball_ncaab_championship_winner
and icehockey_nhl_championship_winner are deliberately left out for now:
- TeamRankings' college football standings page has no national-championship
  column at all (only Bowl Eligible / Win Conf / Undefeated).
- Its college basketball standings page has a "Win Tourn" column, but that
  turned out to be each team's chance of winning its own CONFERENCE
  tournament (auto-bid), not the NCAA national championship - confirmed by
  the probability-sum check in fetch_probabilities.py flagging ~3100% (31
  conferences x 100%, since exactly one team wins each conference's
  tournament) instead of ~100%.
- Its NHL standings page currently has no projections table at all.

Both basketball and football brackets aren't set this far out from their
postseasons, which is presumably why neither has a real title-probability
column yet. Add these back (with a CSV or other probability source) once a
real one exists.
"""

COMPETITIONS = [
    {
        "key": "americanfootball_nfl_super_bowl_winner",
        "name": "NFL Super Bowl",
        "probability_source": {
            "provider": "teamrankings",
            "url": "https://www.teamrankings.com/nfl/projections/standings/",
            "column": "Win SB",
        },
    },
    {
        "key": "basketball_nba_championship_winner",
        "name": "NBA Championship",
        "probability_source": {
            "provider": "teamrankings",
            "url": "https://www.teamrankings.com/nba/projections/standings/",
            "column": "NBA Champs",
        },
    },
    {
        "key": "baseball_mlb_world_series_winner",
        "name": "MLB World Series",
        "probability_source": {
            "provider": "teamrankings",
            "url": "https://www.teamrankings.com/mlb/projections/standings/",
            "column": "WS Champs",
        },
    },
]

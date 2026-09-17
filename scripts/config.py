"""Tracked competitions: odds source (The Odds API sport key) + model
probability source (TeamRankings projections page) for each.

Only competitions with BOTH an active outrights odds market AND a usable
title-probability source are tracked. fetch_odds.py double-checks each
sport key against the live Odds API sports list and skips anything
inactive, so no odds credits are wasted on an off-season competition.

americanfootball_ncaaf_championship_winner and icehockey_nhl_championship_winner
are deliberately left out for now: TeamRankings' college football standings
page has no national-championship-win column (only Bowl Eligible / Win Conf
/ Undefeated), and its NHL standings page currently has no projections table
at all. Add them back (with a CSV or other probability source) once a real
source exists for both.
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
    {
        "key": "basketball_ncaab_championship_winner",
        "name": "NCAA Basketball Championship",
        "probability_source": {
            "provider": "teamrankings",
            "url": "https://www.teamrankings.com/ncaa-basketball/projections/standings/",
            "column": "Win Tourn",
        },
    },
]

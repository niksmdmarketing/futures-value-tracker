"""Competitions (The Odds API sport keys) tracked for futures/outrights value.

Only competitions confirmed active and offering an outrights market should
stay in this list; fetch_odds.py double-checks against the live sports list
and skips anything inactive so no credits are wasted.
"""

COMPETITIONS = [
    "americanfootball_nfl_super_bowl_winner",
    "americanfootball_ncaaf_championship_winner",
    "basketball_nba_championship_winner",
    "basketball_ncaab_championship_winner",
    "baseball_mlb_world_series_winner",
    "icehockey_nhl_championship_winner",
]

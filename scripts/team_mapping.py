"""Explicit lookup tables from TeamRankings team names to The Odds API /
bookmaker team names.

Built from real data (scripts/diagnostics/dump_team_names.py, run
2026-09-17) rather than guessed - each pair below was confirmed present on
both sides. Any team a competition's probability source names that has no
entry here is logged by calculate.py rather than silently dropped: either
a new/renamed team the table needs updating for, or (as with 5 MLB teams
at the time this was built - Colorado, LA Angels, SF Giants, Sacramento,
Washington) a team no tracked AU bookmaker currently lists odds for, so no
edge can be computed for it regardless.
"""

TEAM_NAME_MAP: dict[str, dict[str, str]] = {
    "americanfootball_nfl_super_bowl_winner": {
        "Arizona": "Arizona Cardinals",
        "Atlanta": "Atlanta Falcons",
        "Baltimore": "Baltimore Ravens",
        "Buffalo": "Buffalo Bills",
        "Carolina": "Carolina Panthers",
        "Chicago": "Chicago Bears",
        "Cincinnati": "Cincinnati Bengals",
        "Cleveland": "Cleveland Browns",
        "Dallas": "Dallas Cowboys",
        "Denver": "Denver Broncos",
        "Detroit": "Detroit Lions",
        "Green Bay": "Green Bay Packers",
        "Houston": "Houston Texans",
        "Indianapolis": "Indianapolis Colts",
        "Jacksonville": "Jacksonville Jaguars",
        "Kansas City": "Kansas City Chiefs",
        "LA Chargers": "Los Angeles Chargers",
        "LA Rams": "Los Angeles Rams",
        "Las Vegas": "Las Vegas Raiders",
        "Miami": "Miami Dolphins",
        "Minnesota": "Minnesota Vikings",
        "NY Giants": "New York Giants",
        "NY Jets": "New York Jets",
        "New England": "New England Patriots",
        "New Orleans": "New Orleans Saints",
        "Philadelphia": "Philadelphia Eagles",
        "Pittsburgh": "Pittsburgh Steelers",
        "San Francisco": "San Francisco 49ers",
        "Seattle": "Seattle Seahawks",
        "Tampa Bay": "Tampa Bay Buccaneers",
        "Tennessee": "Tennessee Titans",
        "Washington": "Washington Commanders",
    },
    "basketball_nba_championship_winner": {
        "Atlanta": "Atlanta Hawks",
        "Boston": "Boston Celtics",
        "Brooklyn": "Brooklyn Nets",
        "Charlotte": "Charlotte Hornets",
        "Chicago": "Chicago Bulls",
        "Cleveland": "Cleveland Cavaliers",
        "Dallas": "Dallas Mavericks",
        "Denver": "Denver Nuggets",
        "Detroit": "Detroit Pistons",
        "Golden State": "Golden State Warriors",
        "Houston": "Houston Rockets",
        "Indiana": "Indiana Pacers",
        "LA Clippers": "Los Angeles Clippers",
        "LA Lakers": "Los Angeles Lakers",
        "Memphis": "Memphis Grizzlies",
        "Miami": "Miami Heat",
        "Milwaukee": "Milwaukee Bucks",
        "Minnesota": "Minnesota Timberwolves",
        "New Orleans": "New Orleans Pelicans",
        "New York": "New York Knicks",
        "Okla City": "Oklahoma City Thunder",
        "Orlando": "Orlando Magic",
        "Philadelphia": "Philadelphia 76ers",
        "Phoenix": "Phoenix Suns",
        "Portland": "Portland Trail Blazers",
        "Sacramento": "Sacramento Kings",
        "San Antonio": "San Antonio Spurs",
        "Toronto": "Toronto Raptors",
        "Utah": "Utah Jazz",
        "Washington": "Washington Wizards",
    },
    "baseball_mlb_world_series_winner": {
        "Arizona": "Arizona Diamondbacks",
        "Atlanta": "Atlanta Braves",
        "Baltimore": "Baltimore Orioles",
        "Boston": "Boston Red Sox",
        "Chi Cubs": "Chicago Cubs",
        "Chi Sox": "Chicago White Sox",
        "Cincinnati": "Cincinnati Reds",
        "Cleveland": "Cleveland Guardians",
        "Detroit": "Detroit Tigers",
        "Houston": "Houston Astros",
        "Kansas City": "Kansas City Royals",
        "LA Dodgers": "Los Angeles Dodgers",
        "Miami": "Miami Marlins",
        "Milwaukee": "Milwaukee Brewers",
        "Minnesota": "Minnesota Twins",
        "NY Mets": "New York Mets",
        "NY Yankees": "New York Yankees",
        "Philadelphia": "Philadelphia Phillies",
        "Pittsburgh": "Pittsburgh Pirates",
        "San Diego": "San Diego Padres",
        "Seattle": "Seattle Mariners",
        "St. Louis": "St. Louis Cardinals",
        "Tampa Bay": "Tampa Bay Rays",
        "Texas": "Texas Rangers",
        "Toronto": "Toronto Blue Jays",
        # Not mapped (no AU bookmaker odds available as of 2026-09-17):
        # Colorado, LA Angels, SF Giants, Sacramento, Washington.
    },
}


def map_team_name(sport_key: str, model_team_name: str) -> str | None:
    return TEAM_NAME_MAP.get(sport_key, {}).get(model_team_name)

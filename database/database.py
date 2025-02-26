from io import StringIO

from teams import teams_table
from players import players_table
from games import games_table
from player_stats import player_stats_table
from users import users_table
from user_picks import user_picks_table
from user_stats import user_stats_table
from user_matchups import user_matchups_table
from version import VersionNumber


###############################################################################


class Database:
    def __init__(self, version_number: VersionNumber, testing=False):
        results = StringIO() if testing else None
        params = [version_number, testing, results]

        self.teams = teams_table(*params)
        self.players = players_table(*params)
        self.games = games_table(*params)
        self.player_stats = player_stats_table(*params)
        self.users = users_table(*params)
        self.user_picks = user_picks_table(*params)
        self.user_stats = user_stats_table(*params)
        self.user_matchups = user_matchups_table(*params)


###############################################################################

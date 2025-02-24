from teams import teams_table
from players import players_table
from games import games_table
from player_stats import player_stats_table
from users import users_table
from user_picks import user_picks_table
from user_stats import user_stats_table
from user_matchups import user_matchups_table


###############################################################################


class Database:
    def __init__(self, version_number):
        self.teams = teams_table(version_number)
        self.players = players_table(version_number)
        self.games = games_table(version_number)
        self.player_stats = player_stats_table(version_number)
        self.users = users_table(version_number)
        self.user_picks = user_picks_table(version_number)
        self.user_stats = user_stats_table(version_number)
        self.user_matchups = user_matchups_table(version_number)


###############################################################################

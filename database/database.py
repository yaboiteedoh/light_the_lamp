import sqlite3
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
        params = [version_number, testing]

        self.teams = teams_table(*params)
        # self.players = players_table(*params)
        # self.games = games_table(*params)
        # self.player_stats = player_stats_table(*params)
        # self.users = users_table(*params)
        # self.user_picks = user_picks_table(*params)
        # self.user_stats = user_stats_table(*params)
        # self.user_matchups = user_matchups_table(*params)

        self.build_sequence = [
            self.teams,
            # self.players,
            # self.games,
            # self.player_stats,
            # self.users,
            # self.user_picks,
            # self.user_stats,
            # self.user_matchups
        ]

        if testing:
            teardown_sequence = build_sequence.reverse()
            for table in teardown_sequence:
                with sqlite3.connect(table.db_dir) as con:
                    cur = con.cursor()
                    sql = f'DROP TABLE {table._table_name}'
                    cur.execute(sql)

            init_dbs(testing, results)
            print(results)


    #------------------------------------------------------# 


    def init_dbs(testing=False, results=None):
        for table in build_sequence:
            table.init_db()
            if testing:
                table._test(results)


###############################################################################

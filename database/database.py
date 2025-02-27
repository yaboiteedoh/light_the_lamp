import sqlite3
from io import StringIO

from .teams import teams_table
from .players import players_table
from .games import games_table
from .player_stats import player_stats_table
from .users import users_table
from .user_picks import user_picks_table
from .user_stats import user_stats_table
from .user_matchups import user_matchups_table
from version import VersionNumber


###############################################################################


class Database:
    def __init__(self, version_number: VersionNumber, testing=False):
        results = StringIO() if testing else None
        params = [version_number, testing]

        self.teams = teams_table(*params)
        self.players = players_table(*params)
        self.games = games_table(*params)
        self.player_stats = player_stats_table(*params)
        # self.users = users_table(*params)
        # self.user_picks = user_picks_table(*params)
        # self.user_stats = user_stats_table(*params)
        # self.user_matchups = user_matchups_table(*params)

        self.build_sequence = [
            self.teams,
            self.players,
            self.games,
            self.player_stats,
            # self.users,
            # self.user_picks,
            # self.user_stats,
            # self.user_matchups
        ]

        if testing:
            try:
                self._test(results)
            except BaseException as e:
                print(results.getvalue())
                raise e


    #------------------------------------------------------# 


    def init_dbs(self, testing=False, results=None):
        for table in self.build_sequence:
            table.init_db()
            if testing:
                table._test(results)


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _test(self, results):
        teardown_sequence = self.build_sequence[::1]
        for table in teardown_sequence:
            with sqlite3.connect(table.db_dir) as con:
                cur = con.cursor()
                sql = f'DROP TABLE {table._table_name}'
                try:
                    cur.execute(sql)
                except sqlite3.OperationalError as e:
                    error = str(e)
                    if error[:13] == 'no such table':
                        print(f'tried dropping nonexistent table: test.{error[15:]}')
                        con.rollback()
                        continue
                else:
                    print(f'dropped table: test.{table._table_name}')

        self.init_dbs(testing=True, results=results)
        print(results.getvalue())


###############################################################################

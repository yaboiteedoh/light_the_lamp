import sqlite3
from io import StringIO

from nhlpy import NHLClient

from .teams import teams_table
from .players import players_table
from .games import games_table
from .player_stats import player_stats_table
from .users import users_table
from .user_picks import user_picks_table
from .user_stats import user_stats_table
from .user_matchups import user_matchups_table
from utils.dataclasses import (
    Team
)
from version import VersionNumber


###############################################################################


class Database:
    def __init__(
        self,
        version_number: VersionNumber,
        nhl: NHLClient,
        testing=False
    ):
        self.nhl = nhl

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
                self._test(results, version_number)
            except Exception as e:
                print(results.getvalue())
                raise e
        else:
            self.init()
            self.populate()


    #------------------------------------------------------# 


    def init(self, testing=False, results=None):
        for table in self.build_sequence:
            try:
                table.init_db()
            except sqlite3.OperationalError as e:
                error = str(e)
                if error[-14:] == 'already exists':
                    continue
                else:
                    raise e
            if testing:
                results.write(f'\n\ninitializing {table._table_name} table')
                table._test(results)


    def populate(self):
        print('\n\tPOPULATING DATABASE\n')

        print('- Populating Teams Table')
        self.teams.populate(self.nhl)
        # for team in self.teams.read_all():
            # print(team)

        print('- Populating Games Tree')
        self.games.populate(
            self.nhl,
            self.teams,
            self.player_stats,
            self.players
        )
        # for game in self.games.read_all():
            # print(game)

        # test_completed = self.nhl.game_center.boxscore(2024020291)
        # test_future = self.nhl.game_center.boxscore(2024021033)
        # print(*test_future.items(), sep='\n')
        # print('\n\n')
        # print(*test_completed.items(), sep='\n')
        # print('\n\n')
        # print(test_future['clock'])
        # print(test_completed['clock'])
        # print(test_completed['periodDescriptor'])
        # print('\n\n')


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _test(self, results, version_number):
        results.write(f'\n\n\tSTARTING DATABASE INTEGRATION TEST\n\tFOR LIGHT_THE_LAMP v{version_number.as_str}\n\n')
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
                        results.write(f'\ntried dropping nonexistent table: test.{error[15:]}')
                        con.rollback()
                        continue
                    else:
                        raise e
                else:
                    results.write(f'\ndropped table: test.{table._table_name}')
        self.init(testing=True, results=results)
        results.write('\n\n')
        print(results.getvalue())


###############################################################################

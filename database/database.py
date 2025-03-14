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
            # self.populate()


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

        print('- Populating Games Tree')
        self.games.populate(
            self.nhl,
            self.teams,
            self.player_stats,
            self.players
        )

        # completed game
        # test_completed = self.nhl.game_center.boxscore(2024020291)
        # live game
        # test_future = self.nhl.game_center.boxscore(2024021042)
        # print(*test_future.items(), sep='\n')
        # print('\n\n')
        # print(*test_completed.items(), sep='\n')
        # print('\n\n')

        # print(test_future['clock'])
        # print(test_completed['clock'])
        # print(test_completed['periodDescriptor'])
        # print('\n\n')


    def get_join_players(self, player_rowid=None, team_rowid=None):
        with sqlite3.connect(self.teams.db_dir) as con:
            cur = con.cursor()
            sql = '''
                SELECT
                    t.code,
                    p.*
                FROM players as p
                INNER JOIN teams as t ON p.team_rowid = t.rowid
            '''

            match (player_rowid is None, team_rowid is None):
                case (True, True):
                    cur.execute(sql)
                    return cur.fetchall()

                case (False, True):
                    sql += '\tWHERE p.rowid=?'
                    cur.execute(sql, (player_rowid,))
                    return cur.fetchone()

                case (True, False):
                    sql += '\tWHERE t.rowid=?'
                    cur.execute(sql, (team_rowid,))
                    return cur.fetchall()

                case (False, False):
                    sql += '\tWHERE p.rowid=? AND t.rowid=?'
                    cur.execute(sql, (player_rowid, team_rowid))
                    return cur.fetchone()


    def get_join_games(
        self,
        game_rowid=None,
        team_rowid=None,
        home_team_rowid=None,
        away_team_rowid=None
        ):
        with sqlite3.connect(self.games.db_dir) as con:
            cur = con.cursor()
            sql = '''
                SELECT 
                    g.rowid,
                    g.status,
                    ht.code,
                    g.home_team_points,
                    at.code,
                    g.away_team_points
                FROM games as g
                INNER JOIN teams as ht ON g.home_team_rowid = ht.rowid
                INNER JOIN teams as at ON g.away_team_rowid = at.rowid
            '''

        if game_rowid is not None:
            sql += '\tWHERE g.rowid=?'
            cur.execute(sql, (game_rowid,))
            return cur.fetchone()

        if team_rowid is not None:
            sql += '\tWHERE ht.rowid=? OR at.rowid=?'
            cur.execute(sql, (team_rowid, team_rowid))
            return cur.fetchall()

        match (
            home_team_rowid is None,
            away_team_rowid is None
        ):
            case (True, True):
                cur.execute(sql)
                return cur.fetchall()

            case (False, False):
                sql += '\tWHERE ht.rowid=? AND at.rowid=?'
                cur.execute(sql, (home_team_rowid, away_team_rowid))
                return cur.fetchall()

            case (False, True):
                sql += '\tWHERE ht.rowid=?'
                cur.execute(sql, (home_team_rowid,))
                return cur.fetchall()

            case (True, False):
                sql += '\tWHERE at.rowid=?'
                cur.execute(sql, (away_team_rowid,))
                return cur.fetchall()


    def get_join_player_stats(
        self,
        game_rowid=None,
        player_nhlid=None,
        team_rowid=None
    ):
        with sqlite3.connect(self.player_stats.db_dir) as con:
            cur = con.cursor()
            sql = '''
                SELECT
                    g.rowid,
                    p.nhlid,
                    t.code,
                    p.position,
                    p.name,
                    s.goals,
                    s.assists,
                    s.hits,
                    s.blocked_shots,
                    s.shots_on_goal
                FROM player_stats as s
                INNER JOIN games as g ON s.game_rowid = g.rowid
                INNER JOIN teams as t ON s.team_rowid = t.rowid
                INNER JOIN players as p ON s.player_nhlid = p.nhlid
            '''
            cur.execute(sql)
            
            match (
                game_rowid is None,
                player_nhlid is None,
                team_rowid is None
            ):
                case (True, True, True):
                    cur.execute(sql)
                    return cur.fetchall()

                case (False, True, True):
                    sql += '\tWHERE g.rowid = ?'
                    cur.execute(sql, (game_rowid,))
                    return cur.fetchall()

                case (True, True, False):
                    sql += '\tWHERE t.rowid = ?'
                    cur.execute(sql, (team_rowid,))
                    return cur.fetchall()

                case (True, False, True):
                    sql += '\tWHERE p.nhlid = ?'
                    cur.execute(sql, (player_nhlid,))
                    return cur.fetchall()

                case (True, False, False):
                    sql += '\tWHERE t.rowid = ? AND p.nhlid = ?'
                    cur.execute(sql, (team_rowid, player_nhlid))
                    return cur.fetchall()

                case (False, True, False):
                    sql += '\tWHERE g.rowid = ? AND t.rowid = ?'
                    cur.execute(sql, (game_rowid, team_rowid))
                    return cur.fetchall()

                case (False, False, True) | (False, False, False):
                    sql += '\tWHERE g.rowid = ? AND p.nhlid = ?'
                    cur.execute(sql, (game_rowid, player_nhlid))
                    return cur.fetchone()


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

import sqlite3
from io import StringIO
from time import time

from nhlpy import NHLClient

from .tables import (
    TeamsTable,
    GamesTable,
    PlayerStatsTable,
    PlayersTable,
    UsersTable,
    UserPicksTable,
    UserStatsTable,
    UserMatchupsTable
)

from utils.dataclasses import (
    JoinGame,
    JoinPlayerStats
)
from version import VersionNumber


###############################################################################


class Database:
    def __init__(
        self,
        version_number: VersionNumber,
        nhl: NHLClient,
        testing=False,
    ):
        self.nhl = nhl

        results = StringIO() if testing else None

        self.teams = TeamsTable(testing)
        self.players = PlayersTable(testing)
        self.games = GamesTable(testing)
        self.player_stats = PlayerStatsTable(testing)
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
            'IMPORTED',
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


    def update_game_states(self):
        games = self.games.read_by_status('FUT')

        for game in games:
            if not game.is_after(time()):
                game.status = 'LIVE'
                self.games.update_status(game)

        if live := self.games.read_by_status('LIVE') != []:
            self.update_games_by_status('LIVE')

        return live


    def update_games_by_status(self, status):
        self.games._compile_games_by_status(
            status,
            self.nhl,
            self.teams,
            self.player_stats,
            self.players
        )


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
            cur.row_factory = self._join_game_row_factory
            sql = '''
                SELECT 
                    g.rowid,
                    g.status,
                    ht.code as ht_code,
                    g.home_team_points as ht_points,
                    at.code as at_code,
                    g.away_team_points as at_points,
                    g.start_time
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
            cur.row_factory = self._join_player_stats_row_factory
            sql = '''
                SELECT
                    g.rowid as game_rowid,
                    g.start_time as game_start_time,
                    p.nhlid as player_nhlid,
                    t.code as team_code,
                    ot.code as opp_code,
                    p.position as player_position,
                    p.name as player_name,
                    s.goals,
                    s.assists,
                    s.hits,
                    s.blocked_shots,
                    s.shots_on_goal
                FROM player_stats as s
                INNER JOIN games as g ON s.game_rowid = g.rowid
                INNER JOIN teams as t ON s.team_rowid = t.rowid
                INNER JOIN teams as ot ON s.opp_rowid = ot.rowid
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
                    sql += '\tWHERE game_rowid = ?'
                    cur.execute(sql, (game_rowid,))
                    return cur.fetchall()

                case (True, True, False):
                    sql += '\tWHERE team_code = ?'
                    cur.execute(sql, (team_rowid,))
                    return cur.fetchall()

                case (True, False, True):
                    sql += '\tWHERE player_nhlid = ?'
                    cur.execute(sql, (player_nhlid,))
                    return cur.fetchall()

                case (True, False, False):
                    sql += '\tWHERE team_code = ? AND player_nhlid = ?'
                    cur.execute(sql, (team_code, player_nhlid))
                    return cur.fetchall()

                case (False, True, False):
                    sql += '\tWHERE game_rowid = ? AND team_code = ?'
                    cur.execute(sql, (game_rowid, team_code))
                    return cur.fetchall()

                case (False, False, True) | (False, False, False):
                    sql += '\tWHERE game_rowid = ? AND player_nhlid = ?'
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


    def _join_game_row_factory(self, cur, row):
        fields = [column[0] for column in cur.description]
        as_dict = {key: value for key, value in zip(fields, row)}
        return JoinGame(**as_dict)

    
    def _join_player_stats_row_factory(self, cur, row):
        fields = [column[0] for column in cur.description]
        as_dict = {key: value for key, value in zip(fields, row)}
        return JoinPlayerStats(**as_dict)


###############################################################################

import sqlite3
from pathlib import Path
from io import StringIO
from datetime import datetime
from time import sleep

from utils.classes import SQLiteTable
from utils.dataclasses import Game, Player


###############################################################################


CURRENT_SEASON="20242025"
banned_codes = ['MUN']


test_data = [
    {
        'timestamp': 'test',
        'nhlid': 4,
        'start_time': 'test',
        'status': 'active',
        'home_team_rowid': 1,
        'away_team_rowid': 2,
        'home_team_points': 0,
        'away_team_points': 0
    },
    {
        'timestamp': 'test',
        'nhlid': 5,
        'start_time': 'test',
        'status': 'active',
        'home_team_rowid': 1,
        'away_team_rowid': 3,
        'home_team_points': 0,
        'away_team_points': 0
    },
    {
        'timestamp': 'test',
        'nhlid': 6,
        'start_time': 'test',
        'status': 'active',
        'home_team_rowid': 1,
        'away_team_rowid': 4,
        'home_team_points': 0,
        'away_team_points': 0
    },
    {
        'timestamp': 'test',
        'nhlid': 7,
        'start_time': 'test',
        'status': 'active',
        'home_team_rowid': 3,
        'away_team_rowid': 4,
        'home_team_points': 0,
        'away_team_points': 0
    }
]


###############################################################################


class GamesTable(SQLiteTable):
    def __init__(self, testing=False):
        if not testing:
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'test.db'))
        self.dataclass = Game

        self._table_name = 'games'
        self._group_keys = {
            'status': self.read_by_status,
            'team_rowid': self.read_by_team_rowid,
        }
        self._object_keys = {
            'nhlid': self.read_by_nhlid
        }
        self._test_data = test_data


    #------------------------------------------------------# 

    def init_db(self):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE games(
                    timestamp INTEGER NOT NULL,
                    nhlid INTEGER NOT NULL,
                    start_time INTEGER NOT NULL,
                    status STR NOT NULL,
                    home_team_rowid INTEGER NOT NULL,
                    away_team_rowid INTEGER NOT NULL,
                    home_team_points INTEGER NOT NULL,
                    away_team_points INTEGER NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,

                    FOREIGN KEY(home_team_rowid)
                        REFERENCES teams(rowid)
                    FOREIGN KEY(away_team_rowid)
                        REFERENCES teams(rowid)
                )
            '''
            cur.execute(sql)


    def populate(self, status, nhl, teams, player_stats, players):
        self._update_games(nhl, teams)
        self._compile_games_by_status(
            status,
            nhl,
            teams,
            player_stats,
            players
        )


    #------------------------------------------------------# 


    def add(self, game: Game) -> int:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                INSERT INTO games(
                    timestamp,
                    nhlid,
                    start_time,
                    status,
                    home_team_rowid,
                    away_team_rowid,
                    home_team_points,
                    away_team_points
                )
                VALUES (
                    :timestamp,
                    :nhlid,
                    :start_time,
                    :status,
                    :home_team_rowid,
                    :away_team_rowid,
                    :home_team_points,
                    :away_team_points
                )
            '''
            cur.execute(sql, game.as_dict)
            return cur.lastrowid


    #------------------------------------------------------# 


    def read_all(self) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> Game:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_status(self, status: str) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE status=?'
            cur.execute(sql, (status,))
            return cur.fetchall()


    def read_by_start_time(self, start_time: int) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE start_time=?'
            cur.execute(sql, (start_time,))
            return cur.fetchall()
    

    def read_by_team_rowid(self, rowid: int) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = f'''
                SELECT * FROM games
                WHERE home_team_rowid=?
                OR away_team_rowid=?
            '''
            cur.execute(sql, (rowid, rowid))
            return cur.fetchall()


    def read_by_nhlid(self, nhlid: int) -> Game:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE nhlid=?'
            cur.execute(sql, (nhlid,))
            return cur.fetchone()


    #------------------------------------------------------# 


    def update_score(self, game: Game, nhl, boxscore):
        if boxscore['gameState'] != 'PRE':
            s = {
                'rowid': game.rowid,
                'home_team_points':  boxscore['homeTeam']['score'],
                'away_team_points': boxscore['awayTeam']['score']
            }
            with sqlite3.connect(self.db_dir) as con:
                cur = con.cursor()
                sql = '''
                    UPDATE games
                    SET
                        home_team_points=:home_team_points,
                        away_team_points=:away_team_points
                    WHERE rowid=:rowid
                '''
                cur.execute(sql, s)
                con.commit()


    def update_status(self, game: Game):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                UPDATE games
                SET
                    status=?
                WHERE rowid=?
            '''
            cur.execute(sql, (game.status, game.rowid))
            con.commit()
        

###############################################################################


    def _update_games(self, nhl, teams):
        for team in teams.read_all():
            schedule = nhl.schedule.get_season_schedule(
                team_abbr=team.code,
                season=CURRENT_SEASON
            )
            for game in schedule['games']:
                # print(*game.items(), sep='\n')
                if game['gameType'] == 1:
                    continue

                timestamp = datetime.now().timestamp()
                start_time = datetime.strptime(
                    game['startTimeUTC'],
                    '%Y-%m-%dT%H:%M:%SZ'
                ).timestamp() - (60 * 60 * 4)

                status = game['gameState']
                if status == 'OFF':
                    status = 'IMPORTED'

                if game['awayTeam']['abbrev'] in banned_codes:
                    continue
                if game['homeTeam']['abbrev'] in banned_codes:
                    continue
                away_team = teams.read_by_code(game['awayTeam']['abbrev'])
                home_team = teams.read_by_code(game['homeTeam']['abbrev'])

                if away_team is None or home_team is None:
                    print(game)

                game_data = [
                    timestamp,
                    game['id'],
                    start_time,
                    status,
                    home_team.rowid,
                    away_team.rowid,
                ]
                game_obj = Game(*game_data)

                res = self.read_by_nhlid(game_obj.nhlid)
                if res is not None:
                    if res.status == 'COMPILED':
                        continue

                    game_obj.rowid = res.rowid
                    self.update_status(game_obj)
                    continue

                self.add(game_obj)

            else:
                print(f'-- Imported {CURRENT_SEASON} {team.name} games')


    def _compile_games_by_status(self, query_status, nhl, teams, player_stats, players):
        all_games = self.read_all()
        games = [
            game for game in all_games
            if game.status == query_status
        ]
        if games == []:
            print(f'No {query_status} Games to Update')
            return

        for i, game in enumerate(games):
            home_team = teams.read_by_rowid(game.home_team_rowid)
            away_team = teams.read_by_rowid(game.away_team_rowid)

            print(f'{query_status} {i + 1}/{len(games)}/{len(all_games)}')
            boxscore = nhl.game_center.boxscore(game.nhlid)
            status = boxscore['gameState']
            self.update_score(game, nhl, boxscore)

            game.status = status

            if game.status == 'CRIT':
                game.status = 'LIVE'

            if game.status == 'OFF':
                game.status = 'IMPORTED'

            self.update_status(game)

            game = self.read_by_rowid(game.rowid)
            print(f'\t{away_team.code} ({game.away_team_points}) @ {home_team.code} ({game.home_team_points})')

            try:
                stats = boxscore['playerByGameStats']
            except KeyError:
                stats = {}

            for team, roster in stats.items():
                if team == 'awayTeam':
                    opp_team = boxscore['homeTeam']['abbrev']
                else:
                    opp_team = boxscore['awayTeam']['abbrev']
                opp_team = teams.read_by_code(opp_team)
                db_team = teams.read_by_code(boxscore[team]['abbrev'])
                for position, skater_list in roster.items():
                    if position == 'goalies':
                        continue

                    for skater in skater_list:
                        player_stats.update_by_game(
                            boxscore,
                            skater,
                            db_team.rowid,
                            opp_team.rowid,
                            game.rowid
                        )
                        players.update_by_game(game, skater, team)

            match query_status:
                case 'IMPORTED':
                    game.status = 'COMPILED'
                    self.update_status(game)
                case 'LIVE' | 'FINAL':
                    pass
                case _:
                    raise NotImplementedError


###############################################################################


def games_table(testing=False):
    return GamesTable(testing)


###############################################################################

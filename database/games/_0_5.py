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
                    timestamp TEXT NOT NULL,
                    nhlid INTEGER NOT NULL,
                    start_time STR NOT NULL,
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


    def populate(self, nhl, teams, player_stats, players):
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
                ).timestamp()

                status = 'IMPORTED' if game['gameState'] == 'OFF' else game['gameState']

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

        games = self.read_by_status('IMPORTED')
        if games == []:
            print('No Games to Update')
            return
        all_games = self.read_all()
        for i, game in enumerate(games):
            home_team = teams.read_by_rowid(game.home_team_rowid)
            away_team = teams.read_by_rowid(game.away_team_rowid)
            print(f'-- Compiling boxscore data for Game {i + 1}/{len(games)}/{len(all_games)}')
            boxscore = nhl.game_center.boxscore(game.nhlid)
            stats = boxscore['playerByGameStats']
            self.update_score(game, nhl, boxscore)
            game = self.read_by_rowid(game.rowid)
            print(f'--- {away_team.code} ({game.away_team_points}) @ {home_team.code} ({game.home_team_points})')
            for team, roster in stats.items():
                db_team = teams.read_by_code(boxscore[team]['abbrev'])
                for position, skater_list in roster.items():
                    if position == 'goalies':
                        continue
                    for skater in skater_list:
                        player_stats.update_by_game(
                            boxscore,
                            skater,
                            db_team.rowid,
                            game.rowid
                        )
                        players.update_by_game(game, skater, team)
     
            game.status = 'COMPILED'
            self.update_status(game)


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

    
    def read_by_team_rowid(self, rowid: int) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            results = []
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            for option in ['home', 'away']:
                sql = f'SELECT * FROM games WHERE {option}_team_rowid=?'
                cur.execute(sql, (rowid,))
                for result in cur.fetchall():
                    results.append(result)
            return results


    def read_by_nhlid(self, nhlid: int) -> Game:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM games WHERE nhlid=?'
            cur.execute(sql, (nhlid,))
            return cur.fetchone()


    #------------------------------------------------------# 

    def update_score(self, game: Game, nhl, boxscore):
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


def games_table(testing=False):
    return GamesTable(testing)


###############################################################################

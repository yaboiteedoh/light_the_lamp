import sqlite3
from pathlib import Path
from io import StringIO

from utils.classes import SQLiteTable
from utils.dataclasses import Game


###############################################################################


test_data = [
    {
        'timestamp': 'test',
        'nhlid': 4,
        'start_time': 'test',
        'status': 'active',
        'home_team_rowid': 1,
        'away_team_rowid': 2,
        'clock': 'test',
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
        'clock': 'test',
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
        'clock': 'test',
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
        'clock': 'test',
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
                    clock TEXT NOT NULL,
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
                    clock,
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
                    :clock,
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


###############################################################################


def games_table(testing=False):
    return GamesTable(testing)


###############################################################################

import sqlite3
from dataclasses import dataclass, field, asdict
from paths import Path
from io import StringIO

from utils.classes import SQLiteTable


###############################################################################


test_data = []


###############################################################################


class GamesTable(SQLiteTable):
    def __init__(self, testing=False, results=None):
        if not testing:
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'testing', 'data.db'))
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
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT

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
                    away_team_points,
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
                    :away_team_points,
                )
            '''
            cur.execute(sql, **game.as_dict)
            return cur.lastrowid


    #------------------------------------------------------# 


    def read_all(self) -> list[Game]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players'
            cur.execute(sql)
            return cur.fetchall


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
                cur.execute(sql, (status,))
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


#-----------------------------------------------------------------------------#


@dataclass(slots=True)
class Game:
    timestamp: str
    nhlid: int
    start_time: str
    status: str
    home_team_rowid: int
    away_team_rowid: int
    clock: str = field(default='n/a')
    home_team_points: int = field(default=0)
    away_team_points: int = field(default=0)
    rowid: int | None = field(default=None)

    @property
    def as_dict(self):
        asdict(self)


###############################################################################


def games_table(testing=False, results=None):
    return GamesTable(testing, results)


###############################################################################

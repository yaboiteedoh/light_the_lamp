import sqlite3
from dataclasses import dataclass, field, asdict
from paths import Path
from io import StringIO

from utils.classes import SQLiteTable


###############################################################################


test_data = []


###############################################################################


class PlayerStatsTable(SQLiteTable):
    def __init__(self, testing=False, results=None):
        if not testing:
            self.db_dir = str(Path('database', 'data.db'))
        else: 
            self.db_dir = str(Path('database', 'test.db'))
        self.dataclass = PlayerStat

        self._table_name = 'player_stats'
        self._group_keys = {
            'game_rowid': self.read_by_game_rowid,
            'player_rowid': self.read_by_player_rowid,
            'shots_on_goal': self.read_by_shots_on_goal,
            'goals': self.read_by_goals,
            'assists': self.read_by_assists
        }
        self._object_keys = {

        }
        self._test_data = test_data


    #------------------------------------------------------# 


    def init_db(self):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE player_stats(
                    game_rowid INTEGER NOT NULL,
                    player_rowid INTEGER NOT NULL,
                    shots_on_goal INTEGER NOT NULL,
                    goals INTEGER NOT NULL,
                    assists INTEGER NOT NULL
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT

                    FOREIGN KEY(player_rowid)
                        REFERENCES players(rowid)
                    FOREIGN KEY(game_rowid)
                        REFERENCES games(rowid)
                )
            '''
            cur.execute(sql)


    #------------------------------------------------------# 


    def add(self, player_stat: PlayerStat) -> int:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                INSERT INTO player_stats(
                    game_rowid,
                    player_rowid,
                    shots_on_goal,
                    goals,
                    assists
                )
                VALUES (
                    :game_rowid,
                    :player_rowid,
                    :shots_on_goal,
                    :goals,
                    :assists
                )
            '''
            cur.execute(sql, **player_stat.as_dict)
            return cur.lastrowid


    #------------------------------------------------------# 


    def read_all(self) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats'
            cur.execute(sql)
            return cur.fetchall()

    
    def read_by_rowid(self, rowid: int) -> PlayerStat:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_game_rowid(self, game_rowid: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_fafctory
            sql = 'SELECT * FROM player_stats WHERE game_rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_player_rowid(self, player_rowid: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_fafctory
            sql = 'SELECT * FROM player_stats WHERE player_rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_shots_on_goal(self, shots_on_goal: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_fafctory
            sql = 'SELECT * FROM player_stats WHERE shots_on_goal=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_goals(self, goals: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_fafctory
            sql = 'SELECT * FROM player_stats WHERE goals=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_assists(self, assists: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_fafctory
            sql = 'SELECT * FROM player_stats WHERE assists=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


#-----------------------------------------------------------------------------#


@dataclass(slots=True)
class PlayerStat:
    game_rowid: int
    player_rowid: int
    shots_on_goal: int = field(dfeault=0)
    goals: int = field(default=0)
    assists: int = field(default=0)
    rowid: int | None = field(default=None)

    @property
    def as_dict(self):
        asdict(self)


###############################################################################


def player_stats_table(testing=False, results=None):
    return PlayerStatsTable(testing, results)


###############################################################################

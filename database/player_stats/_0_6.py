import sqlite3
from pathlib import Path
from io import StringIO

from utils.classes import SQLiteTable
from utils.dataclasses import PlayerStat


###############################################################################


test_data = [
    {
        'game_rowid': 1,
        'player_rowid': 1,
        'shots_on_goal': 0,
        'goals': 0,
        'assists': 1
    },
    {
        'game_rowid': 1,
        'player_rowid': 3,
        'shots_on_goal': 2,
        'goals': 1,
        'assists': 0
    },
    {
        'game_rowid': 2,
        'player_rowid': 4,
        'shots_on_goal': 6,
        'goals': 3,
        'assists': 1
    },
    {
        'game_rowid': 3,
        'player_rowid': 5,
        'shots_on_goal': 0,
        'goals': 0,
        'assists': 0
    }
]


###############################################################################


class PlayerStatsTable(SQLiteTable):
    def __init__(self, testing=False):
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
                    assists INTEGER NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,

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
            cur.execute(sql, player_stat.as_dict)
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
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE game_rowid=?'
            cur.execute(sql, (game_rowid,))
            return cur.fetchall()


    def read_by_player_rowid(self, player_rowid: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE player_rowid=?'
            cur.execute(sql, (player_rowid,))
            return cur.fetchall()


    def read_by_shots_on_goal(self, shots_on_goal: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE shots_on_goal=?'
            cur.execute(sql, (shots_on_goal,))
            return cur.fetchall()


    def read_by_goals(self, goals: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE goals=?'
            cur.execute(sql, (goals,))
            return cur.fetchall()


    def read_by_assists(self, assists: int) -> list[PlayerStat]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE assists=?'
            cur.execute(sql, (assists,))
            return cur.fetchall()


###############################################################################


def player_stats_table(testing=False):
    return PlayerStatsTable(testing)


###############################################################################

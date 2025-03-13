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
        'assists': 1,
        'hits': 0,
        'blocked_shots': 1,
        'shots_on_goal': 0
    },
    {
        'game_rowid': 1,
        'player_rowid': 3,
        'shots_on_goal': 2,
        'goals': 1,
        'assists': 0,
        'hits': 0,
        'blocked_shots': 1,
        'shots_on_goal': 0
    },
    {
        'game_rowid': 2,
        'player_rowid': 4,
        'shots_on_goal': 6,
        'goals': 3,
        'assists': 1,
        'hits': 0,
        'blocked_shots': 1,
        'shots_on_goal': 0
    },
    {
        'game_rowid': 3,
        'player_rowid': 5,
        'shots_on_goal': 0,
        'goals': 0,
        'assists': 0,
        'hits': 0,
        'blocked_shots': 1,
        'shots_on_goal': 0
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
            'player_nhlid': self.read_by_player_rowid,
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
                    player_nhlid INTEGER NOT NULL,
                    team_rowid INTEGER NOT NULL,
                    goals INTEGER NOT NULL,
                    assists INTEGER NOT NULL,
                    hits INTEGER NOT NULL,
                    blocked_shots INTEGER NOT NULL,
                    shots_on_goal INTEGER NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,

                    FOREIGN KEY(player_nhlid)
                        REFERENCES players(nhlid)
                    FOREIGN KEY(game_rowid)
                        REFERENCES games(rowid)
                    FOREIGN KEY(team_rowid)
                        REFERENCES teams(rowid)
                )
            '''
            cur.execute(sql)


    def update_by_game(self, boxscore, skater, team_rowid, game_rowid):
        player_stat_data = [
            game_rowid,
            skater['playerId'],
            team_rowid,
            skater['goals'],
            skater['assists'],
            skater['hits'],
            skater['blockedShots'],
            skater['sog']
        ]
        res = self.read_by_player_and_game_rowids(
            skater['playerId'],
            boxscore['id']
        )
        if res is not None:
            player_stat_data.append(res.rowid)
            self.update(PlayerStat(*player_stat_data))
        else:
            self.add(PlayerStat(*player_stat_data))


    #------------------------------------------------------# 


    def add(self, player_stat: PlayerStat) -> int:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                INSERT INTO player_stats(
                    game_rowid,
                    player_nhlid,
                    team_rowid,
                    shots_on_goal,
                    goals,
                    assists,
                    hits,
                    blocked_shots,
                    shots_on_goal
                )
                VALUES (
                    :game_rowid,
                    :player_nhlid,
                    :team_rowid,
                    :shots_on_goal,
                    :goals,
                    :assists,
                    :hits,
                    :blocked_shots,
                    :shots_on_goal
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
            sql = 'SELECT * FROM player_stats WHERE player_nhlid=?'
            cur.execute(sql, (player_rowid,))
            return cur.fetchall()


    def read_by_player_and_game_rowids(
        self,
        player_rowid: int,
        game_rowid: int
    ) -> PlayerStat:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM player_stats WHERE player_nhlid=? AND game_rowid=?'
            cur.execute(sql, (player_rowid, game_rowid))
            return cur.fetchone()


    #------------------------------------------------------# 


    def update(self, player_stat: PlayerStat):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                UPDATE player_stats
                SET
                    goals=:goals,
                    assists=:assists,
                    hits=:hits,
                    blocked_shots=:blocked_shots,
                    shots_on_goal=:shots_on_goal
                WHERE rowid=:rowid
            '''
            cur.execute(sql, player_stat.as_dict)
            con.commit()



###############################################################################


def player_stats_table(testing=False):
    return PlayerStatsTable(testing)


###############################################################################

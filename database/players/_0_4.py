import sqlite3
from dataclasses import dataclass, field, asdict
from paths import Path
from io import StringIO

from utils.classes import SQLiteTable


###############################################################################


test_data = [
    {
        "nhlid": 5,
        "team_rowid": 9,
        "status": "active",
        "name": "Patrick Kane"
    },
    {
        "nhlid": 6,
        "team_rowid": 9,
        "status": "active",
        "name": "Sebastian Aho"
    },
    {
        "nhlid": 7,
        "team_rowid": 10,
        "status": "inactive",
        "name": "Sebastian Aho"
    },
    {
        "nhlid": 8,
        "team_rowid": 9,
        "status": "inactive",
        "name": "Dylan Larkin"
    }
]


###############################################################################


class PlayersTable(SQLiteTable):
    def __init__(self, testing=False, results=None):
        if not testing:
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'test.db'))
        self.dataclass = Player

        self._table_name = 'players'
        self._group_keys = {
            'team_rowid': self.read_by_team_rowid,
            'status': self.read_by_status,
            # There are a few active players who share names
            'name': self.read_by_name
        }
        self._object_keys = {
            'nhlid': self.read_by_nhlid
        }
        self._test_data = test_data


    #------------------------------------------------------# 


    def init_db(self):
        with sqlite3.connect(self.db_dir) as con:
            self._table_name = 'players'

            cur = con.cursor()
            sql = '''
                CREATE TABLE players(
                    nhlid INTEGER NOT NULL,
                    team_rowid INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    name TEXT NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT

                    FOREIGN KEY(team_rowid)
                        REFERENCES teams(rowid)
                )
            '''
            cur.execute(sql)


    #------------------------------------------------------# 


    def add(self, player: Player) -> int:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                INSERT INTO players(
                    nhlid,
                    team_rowid,
                    status,
                    name
                )
                VALUES (
                    :nhlid,
                    :team_rowid,
                    :roster_status,
                    :player_name
                )
            '''
            cur.execute(sql, **player.as_dict)
            return cur.lastrowid


    #------------------------------------------------------# 


    def read_all(self) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players'
            cur.execute(sql)
            return cur.fetchall()

    
    def read_by_rowid(self, rowid: int) -> Player:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_team_rowid(self, team_rowid: int) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE team=?'
            cur.execute(sql, (team_rowid,))
            return cur.fetchall()


    def read_by_status(self, roster_status: str) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE roster_status=?'
            cur.execute(sql, (rowid,))
            return cur.fetchall()


    def read_by_name(self, name: str) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE player_name=?'
            cur.execute(sql, (rowid,))
            return cur.fetchall()


    def read_by_nhlid(self, nhlid: int) -> Player:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM players WHERE nhlid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


#-----------------------------------------------------------------------------#


@dataclass(slots=True)
class Player:
    nhlid: int
    team_rowid: int
    status: str
    name: str
    rowid: int | None = field(default=None)

    @property
    def as_dict(self):
        return asdict(self)


###############################################################################


def players_table(testing=False, results=None):
    return PlayersTable(testing, results)


###############################################################################

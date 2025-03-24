import sqlite3
from pathlib import Path
from io import StringIO

from utils.classes import SQLiteTable
from utils.dataclasses import Team


###############################################################################


test_data = [
    {
        "conference": "E",
        "division": "M",
        "name": "New York Rangers",
        "code": "NYR",
        "nhlid": 1
    },
    {
        "conference": "E",
        "division": "A",
        "name": "Detroit Red Wings",
        "code": "DET",
        "nhlid": 2
    },
    {
        "conference": "E",
        "division": "A",
        "name": "Boston Bruins",
        "code": "BOS",
        "nhlid": 3
    },
    {
        "conference": "W",
        "division": "P",
        "name": "San Jose Sharks",
        "code": "SJS",
        "nhlid": 4
    }
]


###############################################################################


class TeamsTable(SQLiteTable):
    def __init__(self, testing=False):
        if not testing:
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'test.db'))
        self.dataclass = Team

        self._table_name = 'teams'
        self._group_keys = {
            'conference': self.read_by_conference,
            'division': self.read_by_division
        }
        self._object_keys = {
            'name': self.read_by_name,
            'code': self.read_by_code,
            'nhlid': self.read_by_nhlid
        }
        self._test_data = test_data


    #------------------------------------------------------# 


    def init_db(self):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                CREATE TABLE teams(
                    conference TEXT NOT NULL,
                    division TEXT NOT NULL,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    nhlid INT NOT NULL,
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT
                )
            '''
            cur.execute(sql)


    def populate(self, nhl):
        for team in nhl.teams.teams_info():
            team_data = [
                team['conference']['abbr'],
                team['division']['abbr'],
                team['name'],
                team['abbr'],
                team['franchise_id']
            ]
            team_obj = Team(*team_data)
            if self.read_by_nhlid(team_obj.nhlid) is not None:
                continue
            self.add(team_obj)


    #------------------------------------------------------# 


    def add(self, team: Team) -> int:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                INSERT INTO teams(
                    conference,
                    division,
                    name,
                    code,
                    nhlid
                )
                VALUES (
                    :conference,
                    :division,
                    :name,
                    :code,
                    :nhlid
                )
            '''
            cur.execute(sql, team.as_dict)
            return cur.lastrowid


    #------------------------------------------------------# 


    def read_all(self) -> list[Team]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_conference(self, conference: str) -> list[Team]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE conference=?'
            cur.execute(sql, (conference,))
            return cur.fetchall()


    def read_by_division(self, division: str) -> list[Team]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE division=?'
            cur.execute(sql, (division,))
            return cur.fetchall()
 

    def read_by_name(self, name: str) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE name =?'
            cur.execute(sql, (name,))
            return cur.fetchone()


    def read_by_code(self, team_code: str) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE code=?'
            cur.execute(sql, (team_code,))
            return cur.fetchone()


    def read_by_nhlid(self, nhlid: int) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE nhlid=?'
            cur.execute(sql, (nhlid,))
            return cur.fetchone()


###############################################################################


def teams_table(testing=False):
    return TeamsTable(testing)


###############################################################################

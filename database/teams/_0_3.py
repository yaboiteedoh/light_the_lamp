import sqlite3
from dataclasses import dataclass, field, asdict
from paths import Path
from io import StringIO

from utils.classes import SQLiteTable


###############################################################################


test_data = [
    {
        "conference": "eastern",
        "division": "metropolitan",
        "location": "New York",
        "name": "Rangers",
        "code": "NYR"
    },
    {
        "conference": "eastern",
        "division": "atlantic",
        "location": "Detroit",
        "name": "Red Wings",
        "code": "DET"
    },
    {
        "conference": "eastern",
        "division": "atlantic",
        "location": "Boston",
        "name": "Bruins",
        "code": "BOS"
    },
    {
        "conference": "western",
        "division": "pacific",
        "location": "San Jose",
        "name": "Sharks",
        "code": "SJS"
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
            'code': self.read_by_code
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
                    location TEXT NOT NULL,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT
                )
            '''
            cur.execute(sql)


    #------------------------------------------------------# 


    def add(self, team: Team) -> int:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = '''
                INSERT INTO teams(
                    conference,
                    division,
                    location,
                    name,
                    code
                )
                VALUES (
                    :conference,
                    :division,
                    :location,
                    :name,
                    :code
                )
            '''
            cur.execute(sql, **team.as_dict)
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


    def read_by_code(self, team_code: str) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._dataclass_row_factory
            sql = 'SELECT * FROM teams WHERE code=?'
            cur.execute(sql, (team_code,))
            return cur.fetchone()


#-----------------------------------------------------------------------------#


@dataclass(slots=True)
class Team:
    conference: str
    division: str
    location: str
    name: str
    code: str
    rowid: int | None = field(default=None)

    @property
    def full_name(self):
        return f"{self.location} {self.name}"

    @property
    def as_dict(self):
        return asdict(self)


###############################################################################


def teams_table(testing=False, results=None):
    return TeamsTable(testing, results)


###############################################################################

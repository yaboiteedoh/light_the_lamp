import sqlite3
from dataclasses import dataclass, field, asdict
from paths import Path
from io import StringIO


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


class TeamsTable:
    def __init__(self, testing=False, results=None):
        if not testing:
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'testing', 'teams.db'))
            self._test(results)


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
                    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
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
            cur.row_factory = self._team_row_factory
            sql = 'SELECT * FROM teams'
            cur.execute(sql)
            return cur.fetchall()


    def read_by_conference(self, conference: str) -> list[Team]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._team_row_factory
            sql = 'SELECT * FROM teams WHERE conference=?'
            cur.execute(sql, (conference,))
            return cur.fetchall()


    def read_by_division(self, division: str) -> list[Team]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._team_row_factory
            sql = 'SELECT * FROM teams WHERE division=?'
            cur.execute(sql, (division,))
            return cur.fetchall()


    def read_by_rowid(self, rowid: int) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._team_row_factory
            sql = 'SELECT * FROM teams WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_code(self, team_code: str) -> Team:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._team_row_factory
            sql = 'SELECT * FROM teams WHERE code=?'
            cur.execute(sql, (team_code,))
            return cur.fetchone()


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _team_row_factory(self, cur, row):
        fields = [column[0] for column in cur.description]
        as_dict = {key: value for key, value in zip(fields, row)}
        return Team(**as_dict)


    def _test(self, results: StringIO) -> None:
        self._reset_table()
        results.write('testing teams database')
        
        test_objects = [
            Team(**team)
            for team in test_data
        ]
        
        conferences = {
            team['conference']
            for team in test_data
        }
        teams_by_conference = {conference: [] for conference in conferences}
        for team in test_data:
            conference = team['conference']
            teams_by_conference[conference].append[team]
        
        divisions = {
            team['division']
            for team in test_data
        }
        teams_by_division = {division: [] for division in divisions}
        for team in test_data:
            division = team['division']
            teams_by_division[division].append[team]

        results.write('\n\ttesting teams.add(), teams.read_all()')
        for obj, team in zip(test_objects, test_data):
            team['rowid'] = db.add_support_request(obj)
        
        db_teams = self.read_all()
        _compare_data(results, test_data, db_teams)

        results.write('\n\ttesting teams.read_by_rowid(), teams.read_by_code()')
        for team in test_data:
            obj_rowid = self.read_by_rowid(team['rowid']).as_dict
            _compare_items(team, obj_rowid)
            obj_code = self.read_by_code(team['code']).as_dict
            _compare_items(team, obj_code)

        results.write('\n\ttesting teams.read_by_conference(), teams.read_by_division()')
        for conference in conferences:
            data_list = teams_by_conference[conference]
            db_objs = self.read_by_conference(conference)
            _compare_data(data_list, db_objs)

        for division in divisions:
            data_list = teams_by_division[division]
            db_objs = self.read_by_division(division)
            _compare_data(data_list, db_objs)


    def _reset_table():
        remove(self.db_dir)
        self.init_db()


    def _compare_data(results, data_list, objects_list):
        for i, tup in enumerate(zip(data_list, objects_list)):
            data, obj = tup
            obj = obj.as_dict
            _compare_items(results, data, obj, i)


    def _compare_items(results, data, obj, i=None):
        for key, value in data.items():
            if value != obj[key]:
                error_message = f'''
                    (~)ERROR in test object {i}: key {key}
                        (~~)request value: {value}
                        (~~)type: {type(value)}
                        (~~)object value: {obj[key]}
                        (~~)type: {type(obj[key])}
                '''
                error_message = error_message.replace("    ", "")
                error_message = error_message.replace("(~)", "\t\t")
                error_message = error_message.replace("(~~)", "\t\t\t")
                results.write(error_message)


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


teams_table = TeamsTable()


###############################################################################

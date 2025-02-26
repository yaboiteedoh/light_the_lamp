import sqlite3
from dataclasses import dataclass, field, asdict
from paths import Path
from io import StringIO

from utils.classes import SQLiteTable


###############################################################################


test_data = []


###############################################################################


class PlayersTable(SQLiteTable):
    def __init__(self, testing=False, results=None):
        self._table_name = 'players'
        self._dataclass = Player

        if not testing:
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'testing', 'players.db'))
            self._test(results)


    #------------------------------------------------------# 


    def init_db(self):
        with sqlite3.connect(self.db_dir) as con:
            self._table_name = 'players'

            cur = con.cursor()
            sql = '''
                CREATE TABLE players(
                    nhlid INT NOT NULL,
                    team_rowid INT NOT NULL,
                    roster_status TEXT NOT NULL,
                    player_name TEXT NOT NULL,
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
                    roster_status,
                    player_name
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


    def read_by_team(self, team_rowid: int) -> list[Player]:
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


    # There are a few active players who share names
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


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _test(self, results: StringIO):
        self._reset_table()
        results.write('\ntesting players table')

        # test_objects, \
        # teams, \
        # players_by_team, \
        # status, \
        # players_by_status, \
        # names, \
        # players_by_name = \
        # self._setup_testing_data(test_data)

        results.write('\n\ttesting players.add(), players.read_all()')
        for obj, player in zip(test_objects, test_data):
            player['rowid'] = db.add_support_request(obj)

        db_players = self.read_all()
        self._compare_data(results, test_data, db_teams)

        results.write('\n\ttesting players.read_by_rowid()')
        for player in test_data:
            obj_rowid = self.read_by_rowid(player['rowid']).as_dict
            self._compare_items(results, player, obj_rowid)

        results.write('\n\ttesting players.read_by_team()')
        for team in teams:
            data_list = (players_by_team[team])
            db_objs = self.read_by_team(team)
            self._compare_data(results, data_list, db_objs)

        results.write('\n\ttesting players.read_by_status()')
        for status in statuses:
            data_list = (players_by_status[status])
            db_objs = self.read_by_status(status)
            self._compare_data(results, data_list, db_objs)

        results.write('\n\ttesting players.read_by_name()')
        for name in names:
            data_list = (players_by_name[name])
            db_objs = self.read_by_name(name)
            self._compare_data(results, data_list, db_objs)

        results.write('\n\ttesting players.read_by_nhlid()')
        for player in test_data:
            obj_nhlid = self.read_by_nhlid(player['nhlid'])
            self._compare_items(results, player, obj_nhlid)


        # def self._setup_testing_data(test_data):
        


#-----------------------------------------------------------------------------#


@dataclass(slots=True)
class Player:
    nhlid: int
    team_rowid: int
    roster_status: str
    player_name: str
    rowid: int | None = field(default=None)

    @property
    def as_dict(self):
        return asdict(self)


###############################################################################


def players_table(testing=False, results=None):
    reaturn PlayersTable(testing, results)


###############################################################################

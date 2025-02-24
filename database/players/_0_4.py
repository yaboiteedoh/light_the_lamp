import sqlite3
from dataclasses import dataclass, field, asdict


###############################################################################


class PlayersTable:
    def __init__(self, testing=False, results=None):
        if not testing:
            self.db_dir = str(Path('database', 'data.db'))
        else:
            self.db_dir = str(Path('database', 'testing', 'players.db'))
            self._test(results)


    #------------------------------------------------------# 


    def init_db(self):
        with sqlite3.connect(self.db_dir) as con:
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
            cur.row_factory = self._player_row_factory
            sql = 'SELECT * FROM players'
            cur.execute(sql)
            return cur.fetchall()

    
    def read_by_rowid(self, rowid: int) -> Player:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._player_row_factory
            sql = 'SELECT * FROM players WHERE rowid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    def read_by_team(self, team_rowid: int) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._player_row_factory
            sql = 'SELECT * FROM players WHERE team=?'
            cur.execute(sql, (team_rowid,))
            return cur.fetchall()


    def read_by_status(self, roster_status: str) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._player_row_factory
            sql = 'SELECT * FROM players WHERE roster_status=?'
            cur.execute(sql, (rowid,))
            return cur.fetchall()


    # There are a few active players who share names
    def read_by_name(self, name: str) -> list[Player]:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._player_row_factory
            sql = 'SELECT * FROM players WHERE player_name=?'
            cur.execute(sql, (rowid,))
            return cur.fetchall()


    def read_by_nhlid(self, nhlid: int) -> Player:
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            cur.row_factory = self._player_row_factory
            sql = 'SELECT * FROM players WHERE nhlid=?'
            cur.execute(sql, (rowid,))
            return cur.fetchone()


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _player_row_factory(self, cur, row):
        fields = [column[0] for column in cur.description]
        as_dict = {key: value for key, value in zip(fields, row)}
        return Player(**as_dict)


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

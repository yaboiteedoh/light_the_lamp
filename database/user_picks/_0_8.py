import sqlite3
from dataclasses import dataclass


###############################################################################


class UserPicksTable:
    @property
    def schema(self):
        pass


@dataclass(slots=True)
class UserPick:
    passing: bool


###############################################################################


user_picks_table = UserPicksTable()


###############################################################################

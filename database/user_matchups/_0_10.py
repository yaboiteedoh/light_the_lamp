import sqlite3
from dataclasses import dataclass


###############################################################################


class UserMatchupsTable:
    @property
    def schema(self):
        pass


@dataclass(slots=True)
class UserMatchup:
    passing: bool


###############################################################################


user_matchups_table = UserMatchupsTable()


###############################################################################

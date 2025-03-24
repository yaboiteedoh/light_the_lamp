import sqlite3
from dataclasses import dataclass


###############################################################################


class UsersTable:
    @property
    def schema(self):
        pass


@dataclass(slots=True)
class User:
    passing: bool


###############################################################################


users_table = UsersTable()


###############################################################################

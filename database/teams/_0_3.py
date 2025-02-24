import sqlite3
from dataclasses import dataclass


###############################################################################


class TeamsTable:
    @property
    def schema(self):
        pass


@dataclass(slots=True)
class Team:
    passing: bool


###############################################################################


teams_table = TeamsTable()


###############################################################################

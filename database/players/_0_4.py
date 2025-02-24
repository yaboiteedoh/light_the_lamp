import sqlite3
from dataclasses import dataclass


###############################################################################


class PlayersTable:
    @property
    def schema(self):
        pass


@dataclass(slots=True)
class Player:
    passing: bool


###############################################################################


players_table = PlayersTable()


###############################################################################

import sqlite3
from dataclasses import dataclass


###############################################################################


class GamesTable:
    @property
    def schema(self):
        pass


@dataclass(slots=True)
class Game:
    passing: bool


###############################################################################


games_table = GamesTable()


###############################################################################

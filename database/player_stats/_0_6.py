import sqlite3
from dataclasses import dataclass


###############################################################################


class PlayerStatsTable:
    @property
    def schema(self):
        pass


@dataclass(slots=True)
class PlayerStat:
    passing: bool


###############################################################################


player_stats_table = PlayerStatsTable()


###############################################################################

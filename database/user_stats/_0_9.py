import sqlite3
from dataclasses import dataclass


###############################################################################


class UserStatsTable:
    @property
    def schema(self):
        pass


@dataclass(slots=True)
class UserStat:
    passing: bool


###############################################################################


user_stats_table = UserStatsTable()


###############################################################################

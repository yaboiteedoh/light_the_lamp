from dataclasses import dataclass, field, asdict
from datetime import datetime
from time import time

import pytz

###############################################################################


tz = pytz.timezone('America/Detroit')


###############################################################################


@dataclass(slots=True)
class Team:
    conference: str
    division: str
    name: str
    code: str
    nhlid: int
    rowid: int | None = field(default=None)

    @property
    def full_name(self):
        return f"{self.location} {self.name}"

    @property
    def as_dict(self):
        return asdict(self)


@dataclass(slots=True)
class Player:
    nhlid: int
    team_rowid: int
    name: str
    position: str
    rowid: int | None = field(default=None)

    @property
    def as_dict(self):
        return asdict(self)


@dataclass(slots=True)
class Game:
    timestamp: int
    nhlid: int
    start_time: int
    status: str
    home_team_rowid: int
    away_team_rowid: int
    home_team_points: int = field(default=0)
    away_team_points: int = field(default=0)
    rowid: int | None = field(default=None)

    @property
    def teams(self):
        return [home_team_rowid, away_team_rowid]

    @property
    def local_start_time(self):
        st = datetime.fromtimestamp(self.start_time)
        format = '%m/%d/%y @ %I:%M %p'
        return st.strftime(format)

    @property
    def as_dict(self):
        return asdict(self)


    #------------------------------------------------------# 


    def is_after(self, target: float | int):
        return True if target < self.start_time else False


@dataclass(slots=True)
class PlayerStat:
    game_rowid: int
    player_nhlid: int
    team_rowid: int
    opp_rowid: int
    goals: int = field(default=0)
    assists: int = field(default=0)
    hits: int = field(default=0)
    blocked_shots: int = field(default=0)
    shots_on_goal: int = field(default=0)
    rowid: int | None = field(default=None)

    @property
    def as_dict(self):
        return asdict(self)


@dataclass(slots=True)
class JoinGame:
    rowid: int
    status: str
    ht_code: str
    ht_points: int
    at_code: str
    at_points: str
    start_time: int
 
    @property
    def as_dict(self):
        return asdict(self)

    @property
    def as_tuple(self):
        return (
            self.rowid,
            self.status,
            self.at_code,
            self.at_points,
            self.ht_code,
            self.ht_points,
            self.local_start_time,
        )

    @property
    def local_start_time(self):
        st = datetime.fromtimestamp(self.start_time)
        format = '%m/%d/%y @ %I:%M %p'
        return st.strftime(format)

    @property
    def teams(self):
        return [
            (self.ht_code, self.ht_points),
            (self.at_code, self.at_points)
        ]

    @property
    def winner(self):
        return self.ht_code if self.ht_points > self.at_points else self.at_code


    #------------------------------------------------------# 


    def is_after(self, target: float | int):
        return target < self.start_time


@dataclass(slots=True)
class JoinPlayerStats:
    game_rowid: int
    game_start_time: int
    player_nhlid: int
    team_code: str
    opp_code: str
    player_position: str
    player_name: str
    goals: int
    assists: int
    hits: int
    blocked_shots: int
    shots_on_goal: int

    @property
    def as_dict(self):
        return asdict(self)

    @property
    def as_tuple(self):
        return (
            self.game_rowid,
            self.game_start_time,
            self.player_nhlid,
            self.team_code,
            self.opp_code,
            self.player_position,
            self.player_name,
            self.goals,
            self.assists,
            self.hits,
            self.blocked_shots,
            self.shots_on_goal,
        )

    @property
    def local_start_time(self):
        st = datetime.fromtimestamp(self.game_start_time)
        format = '%m/%d/%Y @ %I:%M %p'
        return st.strftime(format)


###############################################################################

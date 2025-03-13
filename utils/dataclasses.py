from dataclasses import dataclass, field, asdict


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
    timestamp: str
    nhlid: int
    start_time: str
    status: str
    home_team_rowid: int
    away_team_rowid: int
    home_team_points: int = field(default=0)
    away_team_points: int = field(default=0)
    rowid: int | None = field(default=None)

    @property
    def as_dict(self):
        return asdict(self)


@dataclass(slots=True)
class PlayerStat:
    game_rowid: int
    player_nhlid: int
    team_rowid: int
    shots_on_goal: int = field(default=0)
    goals: int = field(default=0)
    assists: int = field(default=0)
    hits: int = field(default=0)
    blocked_shots: int = field(default=0)
    shots_on_goal: int = field(default=0)
    rowid: int | None = field(default=None)

    @property
    def as_dict(self):
        return asdict(self)


###############################################################################

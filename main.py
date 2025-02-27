from nhlpy import NHLClient

from version import get_version_number, update_install_version
from database import Database
from utils.dataclasses import (
    Team,
    Player,
    Game,
    PlayerStat
)

update_install_version()
version = get_version_number()
nhl = NHLClient()
db = Database(version, testing=True)

def main():
    for team in nhl.teams.teams_info():
        pass

if __name__ == '__main__':
    main()

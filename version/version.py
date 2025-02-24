import json
from pathlib import Path
from dataclasses import dataclass


###############################################################################


CODE_VERSION = Path('version', 'version.json')
INSTALL_VERSION = Path('version', 'current_version.json')


###############################################################################


@dataclass(slots=True)
class VersionNumber:
    major: int
    minor: int
    development: int

    @property
    def as_tuple(self):
        return (self.major, self.minor, self.development)

    @property
    def as_str(self):
        return f'{self.major}.{self.minor}.{self.development}'

    @property
    def as_dict(self):
        return {'major': major, 'minor': minor, 'development': development}


###############################################################################


def update_install_version():
    with open(CODE_VERSION, 'r') as f:
        data = json.load(f)
    with open(INSTALL_VERSION, 'w') as f:
        json.dump(data, f)


def update_code_version(type='development'):
    with open(CODE_VERSION, 'r') as f:
        data = json.load(f)

    match type:
        case 'major':
            data['major'] += 1
            data['minor'] = 0
            data['development'] = 0
        case 'minor':
            data['minor'] += 1
            data['development'] = 0
        case 'development':
            data['development'] += 1

    with open(CODE_VERSION, 'w') as f:
        json.dump(data, f)


#-----------------------------------------------------------------------------#


def get_version_number(which='install', mock_str='0.0.0') -> VersionNumber:
    match which:
        case 'code':
            path = CODE_VERSION
        case 'install':
            path = INSTALL_VERSION
        case 'mock':
            return VersionNumber(*mock_str.split('.'))
        case _:
            raise ValueError(f'Invalid version type requested: {which}')

    with open(path, 'r') as f:
        data = json.load(f)

    return VersionNumber(**data)


###############################################################################

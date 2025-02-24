def players_table(version_number, testing=False, results=None):
    version_number = version_number.as_tuple

    if version_number >= (0, 4):
        from ._0_4 import players_table as table

    return table(testing, results)


def player_object(version_number, player_dict):
    version_number = version_number.as_tuple

    if version_number >= (0,4):
        from ._0_4 import Player

    return Player(**player_dict)


###############################################################################

def players_table(version_number):
    version_number = version_number.as_tuple

    # if version_number >= (0, 4):
    from ._0_4 import players_table

    return players_table


###############################################################################

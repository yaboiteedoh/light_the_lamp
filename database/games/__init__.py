def games_table(version_number):
    version_number = version_number.as_tuple

    # if version_number >= (0, 5):
    from ._0_5 import games_table

    return games_table


###############################################################################

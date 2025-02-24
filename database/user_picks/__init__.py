def user_picks_table(version_number):
    version_number = version_number.as_tuple

    # if version_number >= (0, 8):
    from ._0_8 import user_picks_table

    return user_picks_table


###############################################################################

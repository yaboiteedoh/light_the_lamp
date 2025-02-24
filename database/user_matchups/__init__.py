def user_matchups_table(version_number):
    version_number = version_number.as_tuple

    # if version_number >= (0, 10):
    from ._0_10 import user_matchups_table

    return user_matchups_table


###############################################################################

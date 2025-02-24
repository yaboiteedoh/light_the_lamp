def user_stats_table(version_number):
    version_number = version_number.as_tuple

    # if version_number >= (0, 9):
    from ._0_9 import user_stats_table

    return user_stats_table


###############################################################################

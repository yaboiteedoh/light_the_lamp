def users_table(version_number):
    version_number = version_number.as_tuple

    # if version_number >= (0, 7):
    from ._0_7 import users_table

    return users_table


###############################################################################

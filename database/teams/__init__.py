def teams_table(version_number, testing=False):
    version_number = version_number.as_tuple

    if version_number >= (0, 3):
        from ._0_3 import teams_table as table

    return table(testing)


###############################################################################

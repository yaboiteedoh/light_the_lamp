def teams_table(version_number, testing=False, results=None):
    version_number = version_number.as_tuple

    if version_number >= (0, 3):
        from ._0_3 import teams_table as table

    return table(testing, results)


def team_object(version_number):
    version_number = version_number.as_tuple

    if version_number >= (0, 3):
        from ._0_3 import Team

    return Team


###############################################################################

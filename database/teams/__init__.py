def teams_table(version_number):
    version_number = version_number.as_tuple

    if version_number >= (0, 3):
        from ._0_3 import teams_table

    return teams_table


def team_object(version_number):
    version_number = version_number.as_tuple

    if version_number >= (0, 3):
        from ._0_3 import Team

    return Team


###############################################################################

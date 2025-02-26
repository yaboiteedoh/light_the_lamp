def player_stats_table(version_number):
    version_number = version_number.as_tuple

    # if version_number >= (0, 6):
    from ._0_6 import player_stats_table

    return player_stats_table


def player_stats_object(version_number, player_stats_dict):
    version_number = version_number.as_tuple

    if version_number >= (0, 6):
        from ._0_6 import PlayerStats

    return PlayerStats(**player_stats_dict)


###############################################################################

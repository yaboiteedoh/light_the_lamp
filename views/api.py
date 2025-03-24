from io import StringIO
from datetime import datetime
from time import time

import pytz
from flask import render_template, request
from flask_htmx import HTMX

from utils.dataclasses import JoinPlayerStats


###############################################################################


format = '%m/%d/%y @ %I:%M:%S %p'
tz = pytz.timezone('America/Detroit')


###############################################################################


class API:
    def __init__(self, app, db):
        self.app = app
        self.db = db
        self.htmx = HTMX(app)


    def games(self):
        games = self.db.get_join_games()
            # if I were to factor out the join tables into a new
            # object I could get more in depth with filtering
            # techniques qithout gumming up the database or api objects

        for field, query in request.args.items():
            match field:
                case 'status':
                    query = query.split(',')
                    games = [
                        game for game in games
                        if game.status in query 
                    ]
                case 'team':
                    query = query.split(',')
                    games = [
                        game for game in games
                        or game.at_code in value
                        if game.ht_code in value
                    ]
                case _:
                    raise NotImplementedError

        return render_template(
            'database/games.html',
            games=sorted(
                games,
                key=lambda game: game.start_time
            ),
            query_string=process_args(request)
        )


    def stats(self):
        queries = request.args.keys()
        stats = []
        if 'game' in queries:
            rowid = int(request.args.get('game'))
            stats = self.db.get_join_player_stats(
                game_rowid=rowid
            )
        if 'single' in queries:
            game, player = request.args.get('single').split(',')
            stats += self.db.get_join_player_stats(
                game_rowid=request.args.get('game'),
                player_nhlid=request.args.get('player')
            )
        if 'player' in queries:
            stats += self.db.get_join_player_stats(
                player_nhlid=request.args.get('player')
            )
        
        stats = {stat.as_tuple for stat in stats}
        stats = [JoinPlayerStats(*stat) for stat in stats]
        sorted_stats = sorted(stats, key=lambda stat: stat.team_code)
        teams = {stat.team_code for stat in stats}
        teams = list(teams)
        return render_template(
            'database/stats.html',
            teams=teams,
            stats=sorted_stats,
            start_time=stats[0].local_start_time if stats != [] else None,
            query_string=process_args(request)
        )


    def upcoming_games(self):
        games = self.db.games.read_by_status('FUT')

        start_times = {
            game.start_time 
            for game in games
            if game.is_after(time())
        }
        start_times = list(start_times)
        start_times.sort()
        next_games = self.db.games.read_by_start_time(start_times[0])
        next_games = [
            self.db.get_join_games(game_rowid=game.rowid)
            for game in next_games
        ]

        return render_template(
            'info/upcoming_games.html',
            query_string=process_args(request),
            start_time=games[0].local_start_time,
            upcoming_games=next_games
        )


    def sync(self):
        live = self.db.update_game_states()

        for status in ['FINAL', 'IMPORTED']:
            self.db.update_games_by_status(status)

        if 'footer' in request.args.keys():
            return render_template(
                'tools/sync_object.html',
                refresh=5 if live else 20,
                timestamp=now()
            )

        return {'success': True, 'live': live}
        

###############################################################################


def now():
    return datetime.now(tz).strftime(format)


def process_args(request):
    query_string = '?'
    for key, value in request.args.items():
        query_string += f'{key}={value}&'
    return query_string[:-1]


###############################################################################

from nhlpy import NHLClient

from flask import Flask

from version import get_version_number, update_install_version
from database import Database
from views import Public, API




update_install_version()
version = get_version_number()

nhl = NHLClient()
db = Database(version, nhl, testing=False)

app = Flask(__name__)
app.config['DEBUG'] = True

app.jinja_options = {"trim_blocks": True, "cache_size": 0}
app.create_jinja_environment()

public = Public(app, db)
api = API(app, db)

app.add_url_rule(
    "/",
    view_func=public.home
)
app.add_url_rule(
    "/database/games",
    view_func=api.games
)
app.add_url_rule(
    "/api/sync",
    view_func=api.sync
)
app.add_url_rule(
    "/database/stats",
    view_func=api.stats
)
app.add_url_rule(
    "/info/upcoming_games",
    view_func=api.upcoming_games
)
test = 'test'

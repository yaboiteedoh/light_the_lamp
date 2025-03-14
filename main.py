from nhlpy import NHLClient

from flask import Flask

from version import get_version_number, update_install_version
from database import Database
from utils.dataclasses import (
    Team,
    Player,
    Game,
    PlayerStat
)
from views import Public

update_install_version()
version = get_version_number()
nhl = NHLClient()
db = Database(version, nhl, testing=False)

app = Flask(__name__)

app.jinja_options = {"trim_blocks": True, "cache_size": 10}
app.create_jinja_environment()

public = Public(app, db)
app.add_url_rule(
    "/",
    view_func=public.home,
    methods=["POST", "GET"]
)
app.add_url_rule(
    "/sync",
    view_func=public.sync,
    methods=["POST", "GET"]
)

from datetime import datetime
from io import StringIO

import pytz
from flask import render_template, request
from flask_htmx import HTMX


###############################################################################


format = '%m/%d/%y @ %I:%M:%S %p'
tz = pytz.timezone('America/Detroit')


###############################################################################


class Public:
    def __init__(self, app, db):
        self.app = app
        self.db = db


    def home(self):
        return render_template(
            'home.html'
        )

###############################################################################


def now():
    return datetime.now(tz).strftime(format)


def process_args(request):
    query_string = '?'
    for key, value in request.args.items():
        query_string += f'{key}={value}&'
    return query_string[:-1]


###############################################################################

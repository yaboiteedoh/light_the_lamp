from flask import render_template



class Public:
    def __init__(self, app, db):
        self.app = app
        self.db = db

    
    def home(self):
        games = []

        for team in self.db.teams.read_all():
            games += self.db.get_join_games(team_rowid=team.rowid)

        return render_template(
            "home.html",
            games=games
        )

    
    def sync(self):
        self.db.populate()
        return self.home()




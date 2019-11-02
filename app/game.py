import functools, requests, yaml, uuid

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)

from app.db import get_db

from app.auth import login_required, admin_required

bp = Blueprint('game', __name__, url_prefix='/game')

class Player:
    def __init__(self):
        self.username = ""
        self.score = 0
        self.lost = 0

    def get_lost(self, max_score):
        self.lost = self.score - max_score

def uuid_to_playername(uuid):
    formula = "SELECT * FROM user WHERE uuid = '{}'".format(uuid)
    db = get_db()
    user = db.execute(formula).fetchone()
    username = "?"
    if user:
        username = user['username']
    return username

@bp.route("/game_details/<game_id>")
@login_required
def game_details(game_id):
    db = get_db()
    formula = "SELECT * FROM game WHERE id = '{}'".format(game_id)
    game = db.execute(formula).fetchone()
    date = game['datestamp']
    formula_players = "SELECT * FROM result WHERE game_uuid = '{}' ORDER BY score DESC".format(game['uuid'])
    fetched_players = db.execute(formula_players).fetchall()
    max_score = fetched_players[0]['score']
    players = []
    for fetched_player in fetched_players:
        player = Player()
        player.username = uuid_to_playername(fetched_player['user_uuid'])
        player.score = fetched_player['score']
        player.get_lost(max_score)
        players.append(player)
    return render_template('game/game_details.html', players=players, date=date)  
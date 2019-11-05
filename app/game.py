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

@bp.route("/details/<game_id>")
@login_required
def details(game_id):
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
    return render_template('game/details.html', players=players, date=date, game_id=game_id)

@bp.route("/remove/<game_id>")
@admin_required
def remove(game_id):
    db = get_db()
    
    formula_game_uuid = "SELECT * FROM game WHERE id = '{}'".format(game_id)
    game_uuid_response = db.execute(formula_game_uuid).fetchone()
    game_uuid = game_uuid_response['uuid']

    if game_uuid:
        formula_remove_link = "DELETE FROM link WHERE game_uuid = '{}'".format(game_uuid)
        db.execute(formula_remove_link)
        formula_remove_results = "DELETE FROM result WHERE game_uuid = '{}'".format(game_uuid)
        db.execute(formula_remove_results)
        formula_remove_game = "DELETE FROM game WHERE uuid = '{}'".format(game_uuid)
        db.execute(formula_remove_game)
        flash("Wynik usunięty")
    else:
        flash("Coś poszło nie tak :/")

    return redirect(url_for("result.winners"))
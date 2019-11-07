import functools, datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, escape, abort, Response, make_response
)

from app.db import get_db

from app.auth import login_required, admin_required

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/change_bg_navbar", methods = ['POST'])
@login_required
def change_bg_navbar():
    response = make_response(redirect(url_for('manage.control_panel')))
    if request.form['bg_navbar_color']:
        color = request.form['bg_navbar_color']
        today = datetime.datetime.now()
        expiration_date = datetime.datetime(today.year + 100, today.month, today.day)
        exp_date_str = expiration_date.strftime("%Y")
        flash("Kolor zmieniony na {}. Zmiana przestanie obowiązywać w roku {}".format(color, exp_date_str))
        response.set_cookie("bg_navbar_color", color, expires=expiration_date)
    return response

@bp.route("/profile/<username>")
@login_required
def profile(username):
    class Curiosity:
        def __init__(self, info, data):
            self.info = info
            self.data = data

    curiosities = []

    try:
        db = get_db()
        user_uuid_formula = "SELECT * FROM user WHERE username = '{}'".format(username)
        user_uuid_reply = db.execute(user_uuid_formula).fetchone()
        user_uuid = user_uuid_reply['uuid']

        # date of the recent won
        last_won_formula = "SELECT * FROM game WHERE winner = '{}'".format(user_uuid)
        last_won_reply = db.execute(last_won_formula).fetchall()
        last_won = "wkrótce"
        if last_won_reply:
            last_won = last_won_reply[-1]['datestamp']
        curiosities.append(Curiosity("Data ostatniego zwycięstwa", str(last_won)))

        # date of last game
        formula_game = "SELECT * FROM result WHERE user_uuid = '{}'".format(user_uuid)
        reply_game = db.execute(formula_game).fetchall()
        game_uuid = reply_game[-1]['game_uuid']
        formula_date = "SELECT * FROM game WHERE uuid = '{}'".format(game_uuid)
        reply_date = db.execute(formula_date).fetchone()
        date = reply_date['datestamp']
        curiosities.append(Curiosity("Data ostatniej rozgrywki", str(date)))

        # best and worst scores
        formula_score = "SELECT * FROM result WHERE user_uuid = '{}' ORDER BY score".format(user_uuid)
        reply_score = db.execute(formula_score).fetchall()
        best_score = reply_score[-1]['score']
        worst_score = reply_score[0]['score']
        curiosities.append(Curiosity("Najlepszy wynik", str(best_score)))
        curiosities.append(Curiosity("Najgorszy wynik", str(worst_score)))

        # average score
        formula_average = "SELECT AVG(score) FROM result WHERE user_uuid = '{}'".format(user_uuid)
        average_score = round(db.execute(formula_average).fetchone()[0],2)
        curiosities.append(Curiosity("Uśredniony wynik", str(average_score)))
    except:
        curiosities.clear()
        curiosities.append(Curiosity("Statystyki dla tego użytkownika nie mogły być wygenerowane", "0"))

    return render_template("user/profile.html", username=username, curiosities=curiosities)
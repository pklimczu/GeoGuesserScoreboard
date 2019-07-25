import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app.db import get_db

bp = Blueprint('result', __name__, url_prefix='/result')

def get_winner_and_results(request_form):
    db = get_db()
    winner = ["",0]
    results = []
    for entry in list(request_form)[1:]:
        user = db.execute('SELECT id, username FROM user WHERE id = ?', (entry.split("_")[-1])).fetchone()
        username = user['username']
        user_id = user['id']
        score = int(request_form[entry])
        results.append((user_id, score))
        if winner[1] < score:
            winner = [username, score]
    return (winner, results)

@bp.route('/add')
def add():
    return render_template('result/add.html')

@bp.route('/all_results')
def all_results():
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    games = db.execute('SELECT * FROM game').fetchall()
    results = db.execute('SELECT * FROM result').fetchall()
    return render_template('result/all_results.html', users=users, games=games, results=results)

@bp.route('/add_manually', methods=('GET', 'POST'))
def add_manually():
    db = get_db()
    if request.method == 'POST':
        played_map = request.form['map']
        winner, results = get_winner_and_results(request.form)
        print("winner", winner)
        print("results", results)
        cur = db.execute(
            'INSERT INTO game (map, winner) VALUES (?, ?)',
             (played_map, winner[0])
        )
        for result in results:
            db.execute(
                'INSERT INTO result (user_id, game_id, score) VALUES (?, ?, ?)',
                (result[0], cur.lastrowid, result[1])
            )
        db.commit()

    users = db.execute('SELECT * FROM user').fetchall()
    return render_template('result/add_manually.html', users=users)
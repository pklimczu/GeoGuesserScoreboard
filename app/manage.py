import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, escape
)

from app.db import get_db

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/users')
def users():
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    return render_template('manage/users.html', users=users)

@bp.route('/dump_database')
def dump_database():
    db = get_db()
    games = db.execute('SELECT * FROM game').fetchall()
    results = db.execute('SELECT * FROM result').fetchall()
    return render_template('manage/dump_database.html', games=games, results=results)

@bp.route('/remove_user/<username>')
def remove_user(username):
    db = get_db()
    username = escape(username)
    formula = "DELETE FROM user WHERE username = '{}'".format(username)
    db.execute(formula)
    db.commit()
    flash("Użytkownik {} został usunięty!".format(username))
    return redirect(url_for('manage.users'))
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, escape, abort
)

from app.db import get_db, init_db_command

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/users')
def users():
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    return render_template('manage/users.html', users=users)

@bp.route('/remove_user/<username>')
def remove_user(username):
    db = get_db()
    username = escape(username)
    formula = "DELETE FROM user WHERE username = '{}'".format(username)
    db.execute(formula)
    db.commit()
    flash("Użytkownik {} został usunięty!".format(username))
    return redirect(url_for('manage.users'))

@bp.route('/dump_database')
def dump_database():
    db = get_db()
    games = db.execute('SELECT * FROM game').fetchall()
    results = db.execute('SELECT * FROM result').fetchall()
    return render_template('manage/dump_database.html', games=games, results=results)

@bp.route('/remove_entry/<database>:<id>')
def remove_entry(database, id):
    database = escape(database)
    id = escape(id)
    formula = "DELETE FROM {} WHERE id = '{}'".format(database, id)
    db = get_db()
    db.execute(formula)
    db.commit()
    flash("Wpis usunięty!")
    return redirect(url_for('manage.dump_database'))

@bp.route('/control_panel')
def control_panel():
    return render_template('manage/control_panel.html')

@bp.route('/reset_db')
def reset_db():
    if g.user['username'] == 'admin':
        print("DUPA")
        init_db_command()
        flash("Baza danych została zresetowana")
        return redirect(url_for('manage.control_panel'))
    else:
        return abort(404)

@bp.route('/create_backup')
def create_backup():
    if g.user['username'] == 'admin':

        return redirect(url_for('manage.control_panel'))
    else:
        return abort(404)

@bp.route('/load_backup')
def load_backup():
    if g.user['username'] == 'admin':

        return redirect(url_for('manage.control_panel'))
    else:
        return abort(404)
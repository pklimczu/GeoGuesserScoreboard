import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, escape, abort, Response
)

from app.db import get_db, init_db_command

bp = Blueprint('manage', __name__, url_prefix='/manage')

def generate_csv(title, database_output):
    text = title + "\n"
    for entry in database_output:
        for field in entry:
            text += str(field)
            text += ","
        text += "\n"
    return text

def generate_backup_file():
    db = get_db()
    users = db.execute("SELECT * FROM user")
    games = db.execute("SELECT * FROM game")
    results = db.execute("SELECT * FROM result")
    csv = "test,test\ntest,test"
    backup_file = generate_csv("user", users)
    backup_file += generate_csv("game", games)
    backup_file += generate_csv("result", results)
    return backup_file

def recreate_from_backup(backup_file):
    db = get_db()
    def restore_user(user):
        [id,username,password,*rest] = user.split(",")
        user_exists = db.execute("SELECT * FROM user WHERE username = '{}'".format(username)).fetchone()
        if not user_exists:
            db.execute("INSERT INTO user (username, password) VALUES ('{}','{}')".format(username, password))
            db.commit()
        else:
            flash("{} istnieje!".format(username))

    def restore_game(game):
        [id,datestamp,played_map,winner,*rest] = game.split(",")
        formula = "INSERT INTO game (datestamp, map, winner) VALUES ('{}','{}','{}')".format(datestamp, played_map, winner)
        db.execute(formula)
        db.commit()

    def restore_result(result):
        [id,user_id,game_id,score,*rest] = result.split(",")
        formula = "INSERT INTO result (user_id, game_id, score) VALUES ({},{},{})".format(user_id, game_id, score)
        db.execute(formula)
        db.commit()

    names =  {"user":restore_user, "game":restore_game, "result":restore_result}
    function = restore_user
    for line in backup_file.split("\n"):
        if line in names:
            function = names[line]
        else:
            if (len(line) > 0):
                function(line)

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

@bp.route('/control_panel', methods=['GET', 'POST'])
def control_panel():
    if request.method == 'POST':
        if 'backup_file' in request.files:
            backup_text = request.files['backup_file'].read().decode('utf-8')
            recreate_from_backup(backup_text)
            return redirect(url_for('manage.control_panel'))
        else:
            flash("Coś tutaj nie gra - plik nie został przesłany")
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
        backup_file = generate_backup_file()
        return Response(
            backup_file,
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=backup.csv"}
        )
    else:
        return abort(404)
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, escape, abort, Response
)

from app.db import get_db, init_db_command

from app.auth import login_required, admin_required

from werkzeug.security import generate_password_hash

bp = Blueprint('manage', __name__, url_prefix='/manage')

@bp.route('/users')
@admin_required
def users():
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    return render_template('manage/users.html', users=users)

@bp.route('/remove_user/<username>')
@admin_required
def remove_user(username):
    db = get_db()
    username = escape(username)
    formula = "DELETE FROM user WHERE username = '{}'".format(username)
    db.execute(formula)
    db.commit()
    flash("Użytkownik {} został usunięty!".format(username))
    return redirect(url_for('manage.users'))

@bp.route('/dump_database')
@admin_required
def dump_database():
    class Dumped:
        pass

    db = get_db()
    table_names = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()
    dumped_data = []

    for table in table_names:
        dumped_table = Dumped()
        dumped_table.name = table['name']
        cursor = db.execute('SELECT * FROM "{}"'.format(dumped_table.name))
        dumped_table.values = cursor.fetchall()
        dumped_table.headers = [tuple[0] for tuple in cursor.description]
        dumped_data.append(dumped_table)
    
    # games = db.execute('SELECT * FROM game').fetchall()
    # results = db.execute('SELECT * FROM result').fetchall()
    return render_template('manage/dump_database.html', dumped_data=dumped_data)

@bp.route('/remove_entry/<database>:<id>')
@admin_required
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
    if request.method == 'POST' and g.user['username'] == 'admin':
        if 'backup_file' in request.files:
            backup_text = request.files['backup_file'].read().decode('utf-8')
            recreate_from_backup(backup_text)
            return redirect(url_for('manage.control_panel'))
        else:
            flash("Coś tutaj nie gra - plik nie został przesłany")
    return render_template('manage/control_panel.html')

@bp.route('/reset_db')
@admin_required
def reset_db():
    if g.user['username'] == 'admin':
        db = get_db()
        db.execute("DELETE FROM result WHERE id > 0")
        db.execute("DELETE FROM game WHERE id > 0")
        db.execute("DELETE FROM link WHERE id > 0")
        db.execute("DELETE FROM user WHERE id > 1")
        db.commit()
        flash("Baza danych została zresetowana")
        return redirect(url_for('manage.control_panel'))
    else:
        return abort(404)

@bp.route('/create_backup')
@admin_required
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

@bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    if len(request.form['password']) < 7:
        flash("Hasło mniejsze niż 7 znaków to popierdółka, nie hasło.")
    else:
        password = generate_password_hash(request.form['password'])
        username = g.user['username']
        db = get_db()
        db.execute("UPDATE user SET password = '{}' WHERE username = '{}'".format(password, username))
        db.commit()
        pas_lenth = str(len(request.form['password']))
        first_char = request.form['password'][0]
        flash("Hasło zostało zmienione. Zaczyna się od {} i ma {} znaków.".format(first_char, pas_lenth))
    return redirect(url_for('manage.control_panel'))

@bp.route('/script1')
@admin_required
def script1():
    return redirect(url_for('manage.control_panel'))
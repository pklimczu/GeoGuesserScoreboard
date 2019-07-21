import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from app.db import get_db

bp = Blueprint('result', __name__, url_prefix='/result')

@bp.route('/add')
def add():
    return render_template('result/add.html')

@bp.route('/add_manually', methods=('GET', 'POST'))
def add_manually():
    if request.method == 'POST':
        print(request.form)
        for entry in request.form:
            print(entry,request.form[entry])
    db = get_db()
    users = db.execute('SELECT * FROM user').fetchall()
    return render_template('result/add_manually.html', users=users)
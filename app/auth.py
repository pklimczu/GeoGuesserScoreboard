import functools, uuid

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, abort
)

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if g.user is not None and g.user['username'] == 'admin':
        if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                db = get_db()
                user_uuid = str(uuid.uuid4())
                error = None

                if not username:
                    error = 'Username is required!'
                elif not password:
                    error = 'Password is required!'
                elif db.execute(
                    'SELECT id FROM user WHERE username = ?', (username,)
                ).fetchone() is not None:
                    error = 'Użytkownik {} jest już stworzony!'.format(username)
                
                if error is None:
                    db.execute(
                        'INSERT INTO user (username, password, uuid) VALUES (?, ?, ?)',
                        (username, generate_password_hash(password), user_uuid)
                    )
                    db.commit()
                    flash("Użytkownik {} dodany!".format(username))
                    return render_template('auth/register.html')
                flash(error)
    else:
        flash("Tylko admin może dodawać użytkowników!")
        return redirect(url_for('index'))

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username!'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password!'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    
    # Set navbar background color
    navbar_bg = request.cookies.get('bg_navbar_color')
    if navbar_bg is not None:
        g.navbar_bg = "#" + navbar_bg

    # Set user
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user and g.user['username'] == 'admin':
            return view(**kwargs)
        else:   
            return abort(404)
    return wrapped_view
import os

from flask import Flask, render_template
from app.db import get_db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        ADM_PASS='test',
        TEMPLATES_AUTO_RELOAD = True
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # index
    @app.route('/')
    def index(error=None):
        if error:
            flash(error)
        return render_template('index.html')

    from . import db, auth, result, manage, user, game
    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(result.bp)
    app.register_blueprint(manage.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(game.bp)

    return app
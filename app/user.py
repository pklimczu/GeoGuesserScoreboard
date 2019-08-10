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
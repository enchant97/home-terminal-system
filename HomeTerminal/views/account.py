from datetime import datetime

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from ..database.dao.exceptions import RowAlreadyExists
from ..database.dao.user import (change_user_password, get_api_key,
                                 new_account, update_usersettings)

account = Blueprint("account", __name__)

@account.route("/newaccount", methods=["POST", "GET"])
@login_required
def newaccount():
    if current_user.username == current_app.config.get("ADMINUSERNAME"):
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")
            birthday = request.form.get("birthday")
            if username and password and birthday:
                try:
                    birthday = datetime.strptime(birthday, "%Y-%m-%d")
                    new_account(username, password, birthday)
                    flash("user created!")
                except RowAlreadyExists:
                    flash("user already exists!", "error")
            else:
                flash("missing required form details", "error")
        return render_template("account/new_account.html")
    return redirect(url_for("main.index"))

@account.route("/changepassword", methods=["POST", "GET"])
@login_required
def changepassword():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        if old_password and new_password:
            if change_user_password(current_user.username, new_password, old_password):
                flash("password changed")
            else:
                flash("password could not be changed", "error")
        else:
            flash("missing required form details", "error")
    return render_template("account/change_password.html", username=current_user.username)

@account.route("/usersettings", methods=["GET", "POST"])
@login_required
def settings():
    username = current_user.username
    if request.method == "POST":
        rem_notif = bool(request.form.get("rem_notif", 0, int))
        fm_notif = bool(request.form.get("fm_notif", 0, int))
        mess_notif = bool(request.form.get("mess_notif", 0, int))
        user_setting = update_usersettings(
            current_user.username, rem_notif, fm_notif, mess_notif)
        flash("updated your settings")
    else:
        user_setting = update_usersettings(current_user.username)
    return render_template("account/user_settings.html", the_settings=user_setting)

@account.route("/api-key")
@login_required
def api_key_manage():
    return render_template("account/api_key.html", key=get_api_key(current_user.username).key)

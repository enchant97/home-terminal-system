import json
from datetime import datetime

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from ..database.dao.dashboard import (get_shortcuts, get_user_shortcuts,
                                      new_shortcut, update_user_shortcut)
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
        hwm_notif = bool(request.form.get("hwm_notif", 0, int))
        fm_notif = bool(request.form.get("fm_notif", 0, int))
        mess_notif = bool(request.form.get("mess_notif", 0, int))
        user_setting = update_usersettings(
            current_user.username, hwm_notif, fm_notif, mess_notif)
        flash("updated your settings")
    else:
        user_setting = update_usersettings(current_user.username)
    return render_template("account/user_settings.html", the_settings=user_setting)

@account.route("/dashboard-settings", methods=["GET", "POST"])
@login_required
def dashboard_settings():
    if request.method == "POST":
        shortcuts_layout = request.form
        for key in shortcuts_layout.keys():
            if shortcuts_layout[key]:
                priority = key.strip("shortcut_")
                update_user_shortcut(current_user.id_, shortcuts_layout[key], priority)
        flash("updated shortcuts layout")
    return render_template(
        "/account/dashboard-settings.html",
        shortcuts=get_shortcuts(),
        user_sc=get_user_shortcuts(current_user.id_))

@account.route("/dashboard-settings/new-shortcut", methods=["GET", "POST"])
@login_required
def dashboard_new_shortcut():
    if request.method == "POST":
        try:
            name = request.form["name"]
            url_endpoint = request.form["url_endpoint"]
            if not request.form["url_variables"]:
                url_variables = {}
            else:
                url_variables = json.loads(request.form["url_variables"])
            new_shortcut(name, url_endpoint, **url_variables)
            flash("added new shortcut")
            return redirect("account.dashboard_settings")
        except KeyError:
            flash("missing required form values", "error")
    return render_template("/account/new-shortcut.html")


@account.route("/api-key")
@login_required
def api_key_manage():
    return render_template("account/api_key.html", key=get_api_key(current_user.username).key)

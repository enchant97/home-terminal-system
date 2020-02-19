from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from ..dao import RowAlreadyExists, change_user_password, new_account
from ..models import User_Settings, db

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

@account.route("/usersettings", methods=["GET","POST"])
@login_required
def settings():
    #TODO: move database stuff into DAO
    username = current_user.username
    if request.method == "POST":
        try:
            hwm_notif = request.form.get("hwm_notif", 0, int)
            fm_notif = request.form.get("fm_notif", 0, int)
            mess_notif = request.form.get("mess_notif", 0, int)
            User_Settings.query.filter_by(username=username).update(
                dict(hwm_notif=hwm_notif, fm_notif=fm_notif, mess_notif=mess_notif))
            db.session.commit()
            flash("Saved!")
        except:
            logging.exception("usersetting error")
            flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")
    user_settings = User_Settings.query.filter_by(username=username).first()
    return render_template("account/user_settings.html", the_settings=user_settings)
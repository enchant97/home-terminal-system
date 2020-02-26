from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..dao import try_login_user
from ..models import User

main = Blueprint("main", __name__)

@main.route("/", methods=["POST", "GET"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home.dashboard"))
    #TODO: remove User.query.all()
    return render_template("main/index.html", users=User.query.all())

@main.route("/login", methods=["POST"])
def do_login():
    if current_user.is_authenticated:
        return redirect(url_for("home.dashboard"))
    username = request.form.get("username")
    password = request.form.get("password")
    remember_me = request.form.get("rememberme", False)
    if not username or not password:
        flash("You have left the form blank", "warning")
    user = try_login_user(username, password)
    if user:
        if remember_me:
            login_user(user, remember=True)
        else:
            login_user(user, remember=False)
        return redirect(url_for("home.dashboard"))
    flash("username or password not correct", "warning")
    return redirect(url_for(".index"))

@main.route("/logout")
@login_required
def do_logout():
    logout_user()
    flash("You have now logged out")
    return redirect(url_for(".index"))

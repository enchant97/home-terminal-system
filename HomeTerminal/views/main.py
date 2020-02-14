from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..dao import try_login_user
from ..models import User, db

main = Blueprint("main", __name__)

@main.route("/", methods=["POST", "GET"])
def index():
    if current_user.is_authenticated:
            return redirect(url_for("home.dashboard"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("You have left the form blank", "warning")
        user = try_login_user(username, password)
        if user:
            #TODO: change to allow remember me to be chosen on the login form
            login_user(user, remember=True)
            return redirect(url_for("home.dashboard"))
        else:
            flash("username or password not correct", "warning")
    #TODO: remove User.query.all()
    return render_template("login.html", users=User.query.all())

@main.route("/logout")
@login_required
def do_logout():
    logout_user()
    flash("You have now logged out")
    return redirect(url_for(".index"))

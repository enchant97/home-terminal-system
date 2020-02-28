from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from ..dao import get_messages, get_notifations
from ..dao import new_message as newMessage

home = Blueprint("home", __name__)

@home.route("/dashboard")
@login_required
def dashboard():
    username = current_user.username
    notifications = get_notifations(username)

    return render_template(
        "home/dashboard.html",
        username=username,
        messages=get_messages(),
        notifications=notifications
        )

@home.route("/newmessage", methods=["POST", "GET"])
@login_required
def new_message():
    if request.method == "POST":
        message = request.form.get("message")
        if message:
            if newMessage(current_user.username, message):
                flash("Message saved!")
        else:
            flash("required form details missing", "error")
    return render_template("home/new_message.html")

@home.route("/timer", methods=["POST", "GET"])
@login_required
def timer():
    #TODO: better implementation later
    return redirect(url_for(".dashboard"))

@home.route("/cc")
@login_required
def command_center():
    #TODO: move admin check into template?
    if current_user.username == current_app.config.get("ADMINUSERNAME"):
        return render_template("home/command_center.html", admin=True)
    return render_template("home/command_center.html", admin=False)

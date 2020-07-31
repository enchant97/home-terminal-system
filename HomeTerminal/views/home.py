from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required

from ..database.dao.dashboard import get_user_shortcuts
from ..database.dao.user import get_messages, get_notifations
from ..database.dao.user import new_message as newMessage
from ..helpers.checkers import is_admin

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
        notifications=notifications,
        shortcuts=get_user_shortcuts(current_user.id_)
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

@home.route("/cc")
@login_required
def command_center():
    return render_template("home/command_center.html", admin=is_admin(current_user.username))

@home.route("/view-plugins")
@login_required
def view_plugins():
    return render_template("home/plugins.html")

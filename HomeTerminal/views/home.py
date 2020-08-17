from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required

from ..database.dao.dashboard import get_user_shortcuts
from ..database.dao.user import get_messages, get_notifations
from ..database.dao.user import new_message as newMessage
from ..helpers.checkers import is_admin
from ..helpers.server_messaging.types import (DBUpdateTypes, MessageTypes,
                                              Payload, ServerMessage)
from ..sockets import message_handler

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
            added_message = newMessage(current_user.username, message)
            if added_message:
                live_update_payload = Payload.create_dbupdate(
                    DBUpdateTypes.ADD,
                    "messages",
                    added_message.id_)
                live_update_mess = ServerMessage(
                    MessageTypes.DB_UPDATE,
                    live_update_payload)
                message_handler.send_message(live_update_mess, app_name="messages")
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

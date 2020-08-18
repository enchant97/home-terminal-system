from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required

from ..database import dao
from ..helpers.server_messaging.types import (DBUpdateTypes, MessageTypes,
                                              Payload, ServerMessage)
from ..sockets import message_handler

messages = Blueprint("messages", __name__)

@messages.route("/newmessage", methods=["POST", "GET"])
@login_required
def new_message():
    if request.method == "POST":
        message = request.form.get("message")
        if message:
            added_message = dao.user.new_message(current_user.username, message)
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
    return render_template("messages/new_message.html")

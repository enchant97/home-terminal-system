# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, request, session, flash, abort, jsonify
from functools import wraps
from flask_socketio import SocketIO, send, emit, ConnectionRefusedError
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import datetime, timedelta
from subprocess import Popen, PIPE
from threading import Timer

from .utils import hash_str, calc_expire_date, Notification
from .config import Config
from .models import (
    db, User, User_Settings, Api_Key, Message,
    FM4_Category, FM4_Item, Homework_Main,
    Homework_Task, PD1_MainLocation,
    PD1_SubLocation, PD1_FullEvent, PD1_UserEvent
    )
from .last_update import LastUpdate

CONFIG = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading") # async_mode 'threading' works better

LAST_HOMEWORK_UPDATE = LastUpdate()
LAST_MESSAGE_UPDATE = LastUpdate()
LAST_FREEZER_MANAGER_UPDATE = LastUpdate()

# START USERAUTH
def web_auth_required(fn):
    """
    decorator
    Used to make sure that the user is
    logged in before allowing access to specific page
    """
    @wraps(fn)
    def wrap(*args, **kwargs):
        if session.get("username", None):
            return fn(*args, **kwargs)
        else:
            flash("You need to login to see this page", "warning")
            return redirect("/")
    return wrap

def web_admin_auth_required(fn):
    """
    decorator
    Used to make sure that the user is
    admin before allowing access to specific page
    """
    @wraps(fn)
    def wrap(*args, **kwargs):
        if session.get("username", None) == CONFIG.get_admin_username():
            return fn(*args, **kwargs)
        else:
            flash("You need to be a admin to see this page", "warning")
            return redirect("/")
    return wrap

def api_auth_required(fn):
    """
    decorator
    Used to make sure that the api key
    or user cookie is used to use api
    """
    @wraps(fn)
    def wrap(*args, **kwargs):
        if session.get("username", None):
            return fn(*args, **kwargs)
        elif Api_Key.query.filter_by(key=request.headers.get("x-api-key", default="", type=str)).scalar():
            return fn(*args, **kwargs)
        else:
            return abort(401)
    return wrap
# END USERAUTH

# START SOCKET

@socketio.on("connect")
def handle_socket_connect():
    if session.get("username", False) == False:
        logging.debug("socket connection denied")
        raise ConnectionRefusedError('unauthorized!')
    else:
        logging.debug(f"socket connection from {session['username']}")

@socketio.on("removemessage")
def handle_socket_removemessage(message):
    """Removes a message from the viewer"""
    message_id = message.get("id", None)
    if message_id:
        try:
            Message.query.filter_by(id_=message_id).update(dict(removed=1))
            db.session.commit()
        except:
            logging.exception("removed message socket error.")

def send_new_message(message_id, message):
    """Sends new message to connected users"""
    with app.app_context():
        message = {"id":message_id, "content":message}
        socketio.emit("new_message", message, broadcast=True)

def do_timer(timer_name):
    # TODO: Finish Timer send
    with app.app_context():
        message = {"timer_name":timer_name}
        socketio.emit("timeralert", message, broadcast=True)

def send_notification(content, category="message", users=None):
    """
    Sends notification to given users, or all if not specified
    args:
        content : the content of the notification
        category : can be error, warning, message
        users : tuple/list containing usernames or None if broadcasting to all
    """
    notification = {"content":content, "category":category}
    if not users:
        socketio.emit("new_notification", notification, broadcast=True)
    else:
        # TODO: code to send to specific people
        pass
# END SOCKET
# START WEB
# START API
@app.route("/api/hwm/hw", methods=["GET"])
@api_auth_required
def api_get_hw():
    last_update = request.args.get("last_update", None)
    if last_update:
        try:
            last_update = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S.%f")
        except:
            return jsonify({"error":"datetime not in correct format of YYYY/MM/DD H:M:S"})
        if LAST_HOMEWORK_UPDATE.is_uptodate(last_update):
            # if the client already is up-to date
            return jsonify({"error": "you already have the latest data", "loaded_data":tuple()})
    due_hw = Homework_Main.query.filter_by(removed=0).order_by(Homework_Main.datedue).all()
    return jsonify(loaded_data=[hw.serialize() for hw in due_hw])

@app.route("/api/messages", methods=["GET"])
@api_auth_required
def api_get_messages():
    messages = Message.query.filter_by(removed=0).all()
    return jsonify(messages=[message.serialize() for message in messages])

@app.route("/get-api-key", methods=["GET"])
@api_auth_required
def get_api_key():
    try:
        username = session.get("username", False)
        api_key = Api_Key.query.filter_by(owner=username).first()
        if not api_key:
            # create an api key if it does not exist
            api_key = Api_Key(key=hash_str(str(datetime.utcnow())), owner=username)
            db.session.add(api_key)
            db.commit()
        return jsonify(key=api_key.key, owner=username)
    except:
        flash(app.config["SERVER_ERROR_MESSAGE"], "error")
        logging.exception("api key creation failed to run")
# END API

# START FM4
# END FM4

# START HW
# END HW

# START PD1
# END PD1
# END WEB

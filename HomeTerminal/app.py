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

CONFIG = None
SERVER_ERROR_MESSAGE = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading") # async_mode 'threading' works better

def create_app(config_file="usersettings.json"):
    """
    Creates the app and configures SQLALCHEMY

    args:
        config_file : where the app config file is stored
    returns:
        Flask app
    """
    global CONFIG, SERVER_ERROR_MESSAGE, app
    CONFIG = Config(config_file)
    SERVER_ERROR_MESSAGE = CONFIG.get_server_error_message()
    app.config["SECRET_KEY"] = CONFIG.get_secretkey()
    app.config["SQLALCHEMY_DATABASE_URI"] = CONFIG.get_db_path()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
    return app

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
            return jsonify({"error": "You need a valid apikey or usercookie to log in here"})
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
    due_hw = Homework_Main.query.filter_by(removed=0).order_by(Homework_Main.datedue).all()
    return jsonify(homework_due=[hw.serialize() for hw in due_hw])

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
        flash(SERVER_ERROR_MESSAGE, "error")
        logging.exception("api key creation failed to run")
# END API
@app.errorhandler(404)
def not_found(e):
    return render_template("servererror.html", error=e), 404

@app.route("/", methods=["POST", "GET"])
def index():
    try:
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if User.query.filter_by(username=username, password=hash_str(password)).first():
                User.query.filter_by(username=username).update(dict(lastlogin = datetime.now()))
                db.session.commit()
                logging.debug(f"{username} logged in")
                session["username"] = username
                return redirect("/home")
            else:
                flash("username or password not correct", "warning")
        elif session.get("username", False):
            return redirect("/home")
    except:
        logging.exception("Login failed to run.")
    return render_template("login.html", users=User.query.all())


def get_notifations(username):
    """
    returns a generator of all notifications as Notification objects
    """
    usr_setting = User_Settings.query.filter_by(username=username).first()
    if usr_setting.fm_notif == 1:
        week_later = datetime.now() + timedelta(days=7)
        fm_expiring = FM4_Item.query.filter(FM4_Item.expire_date <= week_later).filter_by(removed=0).count()
        if fm_expiring > 0:
            yield Notification(f"You have {fm_expiring} expiring items in the freezer", "warning")
    if usr_setting.hwm_notif == 1:
        hw_due = Homework_Main.query.filter_by(removed=0).count()
        if hw_due > 0:
            yield Notification(f"You have {hw_due} outstanding homeworks", "warning")

@app.route("/home", methods=["GET"])
@web_auth_required
def userhome():
    username = session.get("username", None)
    notifications = get_notifations(username)
    return render_template("/terminal_page.html", username=username, messages=Message.query.filter_by(removed=0).all(), notifications=notifications)

@app.route("/newmessage", methods=["POST", "GET"])
@web_auth_required
def new_message():
    try:
        username = session.get("username", None)
        if request.method == "POST":
            message = request.form["message"]

            the_message = Message(user_from=username, message=message)
            db.session.add(the_message)
            db.session.commit()

            send_new_message(the_message.id_, message)
            flash("Message saved!")
    except:
        flash(SERVER_ERROR_MESSAGE, "error")
        logging.exception("new message failed to run.")
    return render_template("newmessage.html")

@app.route("/timer", methods=["POST", "GET"])
@web_auth_required
def route_timer():
    if request.method == "POST":
        try:
            num_seconds = timedelta(minutes=int(request.form["mins"]), hours=int(request.form["hours"])).seconds
            timer_name = request.form["name"]
            timer = Timer(num_seconds, do_timer, args=(timer_name,))
            timer.daemon = True
            timer.start()
            flash("Timer Started")
        except:
            flash(SERVER_ERROR_MESSAGE, "error")
            logging.exception("new message failed to run.")
        return redirect("/home")
    return render_template("timer.html")

@app.route("/newaccount", methods=["POST", "GET"])
@web_admin_auth_required
def newaccount():
    try:
        if request.method == "POST":
            username = request.form["username"].lower()
            password = hash_str(request.form["password"])
            birthday = datetime.strptime(request.form["birthday"], "%Y-%m-%d")
            if User.query.filter_by(username=username).first():
                flash("username already exists", "warning")
            else:
                new_user = User(username=username, password=password, birthday=birthday)
                db.session.add(new_user)
                db.session.add(User_Settings(username=username))
                db.session.commit()
                flash("user created!")
    except:
        flash(SERVER_ERROR_MESSAGE, "error")
        logging.exception("New account failed to run.")
    return render_template("newaccount.html")

@app.route("/changepassword", methods=["POST", "GET"])
@web_auth_required
def changepassword():
    try:
        username = session.get("username", False)
        if request.method == "POST":
            old_password = hash_str(request.form["old_password"])
            new_password = hash_str(request.form["new_password"])
            the_user = User.query.filter_by(username=username).first()
            if the_user.password == old_password:
                User.query.filter_by(username=username).update(dict(password=new_password))
                db.session.commit()
                flash("saved new password!")
            else:
                flash("incorrect details!", "warning")
    except:
        logging.exception("changepassword error")
        flash(SERVER_ERROR_MESSAGE, "error")
    return render_template("changepassword.html", username=username)

@app.route("/usersettings", methods=["GET","POST"])
@web_auth_required
def get_usersettings():
    username = session.get("username", False)
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
            logging.exception("changepassword error")
            flash(SERVER_ERROR_MESSAGE, "error")
    user_settings = User_Settings.query.filter_by(username=username).first()
    return render_template("usersettings.html", the_settings=user_settings)

@app.route("/logout")
@web_auth_required
def do_logout():
    session.clear()
    flash("logged out")
    return redirect("/")


@app.route("/cc")
@web_auth_required
def command_center():
    if session.get("username", None) == CONFIG.get_admin_username():
        return render_template("commandcenter.html", admin=True)
    return render_template("commandcenter.html", admin=False)

@app.route("/status", methods=["GET"])
@web_admin_auth_required
def server_status():
    sh_path = CONFIG.get_server_status_sh()
    if sh_path:
        status_pipe = Popen(sh_path, shell=True, stdout=PIPE).stdout
        status = status_pipe.read()
    else:
        status = "No Status Available"
    return render_template("admin/status.html", status=status)

@app.route("/server-control", methods=["GET"])
@web_admin_auth_required
def get_servercontrol():
    return render_template("admin/server-control.html")


# START FM4
@app.route("/fm4", methods=["GET", "POST"])
@app.route("/fm4/report", methods=["GET", "POST"])
@web_auth_required
def fm4_report():
    try:
        items = []
        if request.method == "POST":
            category = request.form["category"].capitalize()
            if category == "":
                items = FM4_Item.query.filter_by(removed=0).order_by(FM4_Item.expire_date).all()
            else:
                items = FM4_Item.query.filter_by(categoryname=category, removed=0).order_by(FM4_Item.expire_date).all()
        categories = FM4_Category.query.filter_by(removed=0).all()
        return render_template("fm4/report.html", items=items, categories=categories)
    except:
        logging.exception("fm4 report error")
        flash(SERVER_ERROR_MESSAGE, "error")

@app.route("/fm4/report-expiring", methods=["GET"])
@web_auth_required
def fm4_report_expiring():
    week_later = datetime.now() + timedelta(days=7)
    # gets all items that are about to expire 7 days after todays date or ones that have already expired
    items = FM4_Item.query.filter(FM4_Item.expire_date <= week_later).filter_by(removed=0).order_by(FM4_Item.expire_date).all()
    return render_template("/fm4/report-expiring.html", items=items)

@app.route("/fm4/edit", methods=["GET", "POST"])
@web_auth_required
def fm4_edit():
    try:
        if request.method == "POST":
            id_ = int(request.form.get("id", -1))
            name = request.form["name"]
            amount = request.form["amount"]
            category = request.form["category"].capitalize()
            removed = request.form.get("removed", 0)
            if not FM4_Category.query.filter_by(name=category).scalar():
                db.session.add(FM4_Category(name=category))
                db.session.commit()
            if id_ == -1:
                if request.form.get("custom_expire", False) == "1":
                    expire = datetime.strptime(request.form["expire_date"], "%Y-%m-%d")
                else:
                    expire = calc_expire_date(request.form["expire"])
                
                fm4_item = FM4_Item(name=name, expire_date=expire, categoryname=category, quantity=amount, removed=removed)
                db.session.add(fm4_item)
            else:
                FM4_Item.query.filter_by(id_ = id_).update(dict(name=name, categoryname=category, quantity=amount, removed=removed))
            db.session.commit()
            flash("Added Entry")
        categories = FM4_Category.query.all()
        edit_item_id = request.args.get("item_id", default="", type=str)
        if edit_item_id == "":
            default_item = FM4_Item(name="", expire_date="", categoryname="", quantity=0, id_=-1)
        else: default_item = FM4_Item.query.filter_by(id_=edit_item_id).first()
        return render_template("fm4/edit.html", categories=categories, def_item=default_item)
    except:
        flash(SERVER_ERROR_MESSAGE, "error")
        logging.exception("error with editing fm4")
# END FM4

# START HW
@app.route("/hwm", methods=["GET"])
@app.route("/hwm/view", methods=["GET"])
@web_auth_required
def get_homework():
    try:
        show_removed = request.args.get("showremoved", default=0, type=int)
        due_homework = Homework_Main.query.filter_by(removed=show_removed).order_by(Homework_Main.datedue).all()
        return render_template("/hwm/view_hw.html", due_homework=due_homework)
    except:
        logging.exception("error loading /hwm")
        flash(SERVER_ERROR_MESSAGE, "error")

@app.route("/hwm/view-tasks", methods=["GET"])
@web_auth_required
def get_homework_tasks():
    try:
        homework_id = request.args.get("homework_id", default="", type=str)
        homework_tasks = Homework_Task.query.filter_by(removed=0, hw_id=homework_id).all()
        return render_template("/hwm/view_tasks.html", tasks=homework_tasks, hw_id=homework_id)
    except:
        logging.exception("error loading /hwm")
        flash(SERVER_ERROR_MESSAGE, "error")

@app.route("/hwm/new", methods=["GET", "POST"])
@web_auth_required
def new_homework():
    if request.method == "POST":
        try:
            message = request.form.get("message", None)
            datedue = request.form.get("datedue", None)
            tasks = request.form.getlist("atask")
            logging.debug(f"{message}, {datedue}, {tasks}")
            if message and datedue:
                # if there is content available
                datedue = datetime.strptime(datedue, "%Y-%m-%d")
                new_homework = Homework_Main(message=message, datedue=datedue)
                db.session.add(new_homework)
                db.session.commit()
                if tasks:
                    for task in tasks:
                        db.session.add(Homework_Task(hw_id=new_homework.id_, content=task))
                    db.session.commit()
                flash("added homework")
        except:
            logging.exception("adding new homework error")
            flash(SERVER_ERROR_MESSAGE, "error")
    return render_template("/hwm/new_hw.html")

@app.route("/hwm/new-task", methods=["GET", "POST"])
@web_auth_required
def new_homework_task():
    if request.method == "POST":
        try:
            hw_id = request.form.get("hw_id", None)
            tasks = request.form.getlist("atask")
            if tasks and hw_id:
                for task in tasks:
                    db.session.add(Homework_Task(hw_id=hw_id, content=task))
                db.session.commit()
                flash("added homework tasks")
                redirect("/hwm")
        except:
            logging.exception("adding new homework error")
            flash(SERVER_ERROR_MESSAGE, "error") 
    homework_id = request.args.get("homework_id", default="", type=str)
    return render_template("/hwm/new_tasks.html", hw_id=homework_id)

@app.route("/hwm/remove", methods=["GET"])
@web_auth_required
def remove_homework():
    try:
        homework_id = request.args.get("homework_id", default="", type=str)
        if homework_id:
            Homework_Main.query.filter_by(id_=homework_id).update(dict(removed=1))
            Homework_Task.query.filter_by(hw_id=homework_id).update(dict(removed=1))
            db.session.commit()
    except:
        logging.exception("error removing homework")
        flash(SERVER_ERROR_MESSAGE, "error")
    return redirect("/hwm")

# END HW
# START PD1
@app.route("/pd1/report-subloc", methods=["GET"])
@api_auth_required
def get_pd1_subloc():
    main_loc = request.args.get("mainloc", default="", type=str)
    sublocations = PD1_SubLocation.query.filter_by(main_name=main_loc).all()
    if len(sublocations) > 0:
        return jsonify(main_loc=main_loc, sublocs=[subloc.serialize() for subloc in sublocations])
    return jsonify(sublocs=[])

@app.route("/pd1", methods=["GET", "POST"])
@app.route("/pd1/view", methods=["GET", "POST"])
@web_auth_required
def get_pd1_view():
    loaded_entries = ()
    if request.method == "POST":
        try:
            mainloc = request.form["main-location"].capitalize()
            if request.form.get("all-sub", False) == "1":
                # TODO: allow for user wanting all sub locations
                pass
            else:
                subloc = request.form["sub-location"].capitalize()
                if PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).scalar():
                    subloc = PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).first()
                    loaded_entries = PD1_FullEvent.query.filter_by(subloc=subloc.id_).all()
                else:
                    loaded_entries = ()
        except:
            logging.exception("error viewing pd1")
            flash(SERVER_ERROR_MESSAGE, "error")
    main_locations = PD1_MainLocation.query.order_by(PD1_MainLocation.name).all()
    return render_template("/pd1/view.html", main_locations=main_locations, loaded_entries=loaded_entries)

@app.route("/pd1/edit", methods=["GET", "POST"])
@web_auth_required
def get_pd1_edit():
    if request.method == "POST":
        try:
            mainloc = request.form["mainloc"].capitalize()
            subloc = request.form["subloc"].capitalize()
            datetaken = datetime.strptime(request.form["datetaken"], "%Y-%m-%d")
            notes = request.form["notes"]
            users = request.form.getlist("user", type=str)
            lat = request.form.get("lat", 0, int)
            lng = request.form.get("lng", 0, int)

            if users:
                if not PD1_MainLocation.query.filter_by(name=mainloc).scalar():
                    # add main location if it does not exist
                    db.session.add(PD1_MainLocation(name=mainloc))
                    db.session.commit()
                if not PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).scalar():
                    # add sub location if it does not exist
                    subloc = PD1_SubLocation(name=subloc, main_name=mainloc, lat=lat, lng=lng)
                    db.session.add(subloc)
                    db.session.commit()
                else:
                    subloc = PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).first()
                fullevent = PD1_FullEvent(subloc=subloc.id_, date_taken=datetaken, notes=notes)
                db.session.add(fullevent)
                db.session.commit()
                for user in users:
                    # adds all the user events by selected user
                    db.session.add(PD1_UserEvent(full_event=fullevent.id_, username=user.lower()))
                db.session.commit()
                flash("added entry")
            else:
                flash("not added as no users were selected", "warning")
        except:
            logging.exception("error adding pd1 entry")
            flash(SERVER_ERROR_MESSAGE, "error")
    main_locations = PD1_MainLocation.query.order_by(PD1_MainLocation.name).all()
    return render_template("pd1/edit.html", main_locations=main_locations, users=User.query.filter_by(removed=0).all())
# END PD1
# END WEB

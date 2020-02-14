from datetime import datetime, timedelta

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from ..dao import new_message
from ..models import FM4_Item, Homework_Main, Message, User_Settings, db
from ..utils import Notification

home = Blueprint("home", __name__)

def get_notifations(username):
    """
    returns a generator of all notifications as Notification objects
    """
    #TODO: seperate into DAO
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

@home.route("/dashboard")
@login_required
def dashboard():
    #TODO: seperate into DAO
    username = current_user.username
    notifications = get_notifations(username)

    return render_template(
        "/terminal_page.html",
        username=username,
        messages=Message.query.filter_by(removed=0).all(),
        notifications=notifications
        )

@home.route("/newmessage", methods=["POST", "GET"])
@login_required
def new_message():
    if request.method == "POST":
        message = request.form.get("message")
        if message:
            if new_message(current_user.username, message):
                # TODO: add socketio call in later
                #send_new_message(the_message.id_, message)
                flash("Message saved!")
        else:
            flash("required form details missing", "error")
    return render_template("newmessage.html")

@home.route("/timer", methods=["POST", "GET"])
@login_required
def timer():
    #TODO: better implementation later
    return redirect(url_for(".dashboard"))
    # if request.method == "POST":
    #     try:
    #         num_seconds = timedelta(minutes=int(request.form["mins"]), hours=int(request.form["hours"])).seconds
    #         timer_name = request.form["name"]
    #         timer = Timer(num_seconds, do_timer, args=(timer_name,))
    #         timer.daemon = True
    #         timer.start()
    #         flash("Timer Started")
    #     except:
    #         flash(app.config["SERVER_ERROR_MESSAGE"], "error")
    #         logging.exception("new message failed to run.")
    #     return redirect("/home")
    # return render_template("timer.html")

@home.route("/cc")
@login_required
def command_center():
    #TODO: move admin check into template?
    if current_user.username == current_app.config.get("ADMINUSERNAME"):
        return render_template("commandcenter.html", admin=True)
    return render_template("commandcenter.html", admin=False)

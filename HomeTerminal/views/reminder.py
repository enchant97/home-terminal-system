from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..database.dao.exceptions import RowDoesNotExist
from ..database.dao.reminder import (get_reminder_types, get_reminders,
                                     new_reminder, remove_reminder)
from ..database.dao.user import get_users

reminder = Blueprint("reminder", __name__)

@reminder.route("/view", methods=["GET", "POST"])
@login_required
def view():
    loaded_reminders = ()
    if request.method == "POST":
        try:
            r_type = request.form["reminder-type"]
            show_removed = request.form.get("show-removed", False)
            show_removed = bool(show_removed)
            loaded_reminders = get_reminders(r_type, show_removed)
        except KeyError:
            flash("Missing required form data", "error")
    return render_template(
        "reminder/view.html",
        reminders=loaded_reminders, types=get_reminder_types())

@reminder.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        try:
            content = request.form["reminder-content"]
            user_for = request.form["user-for"]
            r_type = request.form["reminder-type"]
            is_priority = request.form.get("priority", False)
            removed = request.form.get("removed", False)
            new_reminder(content, user_for, r_type, is_priority, removed)
            flash("added entry!")
        except KeyError:
            flash("Missing required form data", "error")
    return render_template(
        "reminder/new.html", users=get_users(),
        reminder_types=get_reminder_types())

@reminder.route("/edit/<reminder_id>", methods=["GET", "POST"])
@login_required
def edit(reminder_id):
    if request.method == "POST":
        removed = request.form.get("removed", False)
        try:
            if removed:
                remove_reminder(reminder_id)
                flash("Entry marked for removal")
            else:
                remove_reminder(reminder_id, False)
                flash("Entry no longer marked for removal")
        except RowDoesNotExist:
            flash("reminder with that id does not exist!", "warning")
        return redirect(url_for(".view"))
    return render_template("/reminder/edit.html")

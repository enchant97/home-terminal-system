from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..database.dao.exceptions import RowDoesNotExist
from ..database.dao.reminder import (get_reminder_tasks, get_reminder_types,
                                     get_reminders, new_reminder,
                                     new_reminder_task, remove_reminder)
from ..database.dao.user import get_users

reminder = Blueprint("reminder", __name__)

@reminder.route("/view", methods=["GET", "POST"])
@login_required
def view():
    loaded_reminders = ()
    if request.method == "POST":
        try:
            r_type_id = request.form["reminder-type"]
            show_removed = request.form.get("show-removed", False)
            show_removed = bool(show_removed)
            if r_type_id:
                loaded_reminders = get_reminders(
                    reminder_type_id=r_type_id,
                    removed=show_removed)
            else:
                loaded_reminders = get_reminders(removed=show_removed)
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
            is_priority = request.form.get("priority", False, bool)
            datedue = request.form.get("datedue")
            tasks = request.form.getlist("atask")
            if datedue:
                # if a date was given
                datedue = datetime.strptime(datedue, "%Y-%m-%d")
            else:
                datedue = None
            added_reminder = new_reminder(
                content, user_for,
                r_type, is_priority, datedue)
            if tasks:
                new_reminder_task(added_reminder.id_, *tasks)
            flash("added entry!")
        except KeyError:
            flash("Missing required form data", "error")
    return render_template(
        "reminder/new.html", users=get_users(),
        reminder_types=get_reminder_types())

@reminder.route("/edit/<int:reminder_id>", methods=["GET", "POST"])
@login_required
def edit(reminder_id):
    if request.method == "POST":
        removed = bool(request.form.get("removed", False))
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
    loaded_reminder = get_reminders(only_first=True, id_=reminder_id)
    loaded_tasks = get_reminder_tasks(reminder_id=reminder_id, removed=False)
    return render_template(
        "/reminder/edit.html",
        reminder=loaded_reminder, tasks=loaded_tasks)

@reminder.route("/edit/<int:reminder_id>/new-task", methods=["GET", "POST"])
@login_required
def new_task(reminder_id):
    if request.method == "POST":
        tasks = request.form.getlist("atask")
        if tasks:
            new_reminder_task(reminder_id, *tasks)
        return redirect(url_for(".edit", reminder_id=reminder_id))
    loaded_reminder = get_reminders(only_first=True, removed=False)
    return render_template("reminder/new_tasks.html", reminder=loaded_reminder)

from datetime import datetime

from flask import (Blueprint, flash, redirect, render_template,
                   request, url_for)
from flask_login import login_required

from ..dao import (RowDoesNotExist, edit_homework, edit_homework_task,
                   get_homework_ordered, get_homework_tasks,
                   mark_homework_for_removal)

hwm = Blueprint("hwm", __name__)

@hwm.route("/")
@login_required
def homework():
    show_removed = request.args.get("showremoved", default=0, type=int)
    due_homework = get_homework_ordered(show_removed)
    return render_template("/hwm/view_hw.html", due_homework=due_homework)

@hwm.route("/view-tasks")
@login_required
def homework_tasks():
    homework_id = request.args.get("homework_id", default="", type=str)
    tasks = get_homework_tasks(homework_id)
    return render_template("/hwm/view_tasks.html", tasks=tasks, hw_id=homework_id)

@hwm.route("/new", methods=["GET", "POST"])
@login_required
def new_homework():
    if request.method == "POST":
        message = request.form.get("message", None)
        datedue = request.form.get("datedue", None)
        tasks = request.form.getlist("atask")

        if message and datedue:
            # if there is content available
            datedue = datetime.strptime(datedue, "%Y-%m-%d")
            the_homework = edit_homework(message, datedue)
            if tasks:
                edit_homework_task(tasks, the_homework.id_)
            flash("added homework")
        else:
            flash("Missing field data!", "warning")
    return render_template("/hwm/new_hw.html")

@hwm.route("/new-task", methods=["GET", "POST"])
@login_required
def new_homework_task():
    if request.method == "POST":
        hw_id = request.form.get("hw_id", None)
        tasks = request.form.getlist("atask")

        if tasks and hw_id:
            edit_homework_task(tasks, hw_id)
            flash("added homework tasks")
        else:
            flash("Missing field data!", "warning")
    homework_id = request.args.get("homework_id", default="", type=str)
    return render_template("/hwm/new_tasks.html", hw_id=homework_id)

@hwm.route("/remove")
@login_required
def remove_homework():
    homework_id = request.args.get("homework_id", default="", type=str)
    if homework_id:
        try:
            mark_homework_for_removal(homework_id)
        except RowDoesNotExist:
            flash(f"homework with that id {homework_id} does not exist!", "error")
    else:
        flash("Missing field data!", "warning")
    return redirect(url_for(".homework"))

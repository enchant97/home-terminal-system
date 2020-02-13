import logging
from datetime import datetime

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import login_required

from ..models import Homework_Main, Homework_Task, db

hwm = Blueprint("hwm", __name__)

@hwm.route("/")
@login_required
def homework():
    #TODO: seperate into DAO
    try:
        show_removed = request.args.get("showremoved", default=0, type=int)
        due_homework = Homework_Main.query.filter_by(removed=show_removed).order_by(Homework_Main.datedue).all()
        return render_template("/hwm/view_hw.html", due_homework=due_homework)
    except:
        logging.exception("error loading /hwm")
        flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")

@hwm.route("/view-tasks")
@login_required
def homework_tasks():
    #TODO: seperate into DAO
    try:
        homework_id = request.args.get("homework_id", default="", type=str)
        homework_tasks = Homework_Task.query.filter_by(removed=0, hw_id=homework_id).all()
        return render_template("/hwm/view_tasks.html", tasks=homework_tasks, hw_id=homework_id)
    except:
        logging.exception("error loading /hwm")
        flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")

@hwm.route("/new", methods=["GET", "POST"])
@login_required
def new_homework():
    #TODO: seperate into DAO
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
            flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")
    return render_template("/hwm/new_hw.html")

@hwm.route("/new-task", methods=["GET", "POST"])
@login_required
def new_homework_task():
    #TODO: seperate into DAO
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
            flash(current_app.config["SERVER_ERROR_MESSAGE"], "error") 
    homework_id = request.args.get("homework_id", default="", type=str)
    return render_template("/hwm/new_tasks.html", hw_id=homework_id)

@hwm.route("/remove")
@login_required
def remove_homework():
    #TODO: seperate into DAO
    try:
        homework_id = request.args.get("homework_id", default="", type=str)
        if homework_id:
            Homework_Main.query.filter_by(id_=homework_id).update(dict(removed=1))
            Homework_Task.query.filter_by(hw_id=homework_id).update(dict(removed=1))
            db.session.commit()
    except:
        logging.exception("error removing homework")
        flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")
    return redirect(url_for(".homework"))

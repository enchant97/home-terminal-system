import logging
from datetime import datetime, timedelta

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required

from ..models import FM4_Category, FM4_Item, db
from ..utils import calc_expire_date

fm4 = Blueprint("fm4", __name__)

#TODO: improve the whole document

@fm4.route("/", methods=["GET", "POST"])
@login_required
def fm4_report():
    #TODO: seperate into DAO
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
        flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")
    return redirect(url_for(".fm4_report"))

@fm4.route("/report-expiring", methods=["GET"])
@login_required
def fm4_report_expiring():
    #TODO: seperate into DAO
    week_later = datetime.now() + timedelta(days=7)
    # gets all items that are about to expire 7 days after todays date or ones that have already expired
    items = FM4_Item.query.filter(FM4_Item.expire_date <= week_later).filter_by(removed=0).order_by(FM4_Item.expire_date).all()
    return render_template("/fm4/report-expiring.html", items=items)

@fm4.route("/edit", methods=["GET", "POST"])
@login_required
def fm4_edit():
    #TODO: seperate into DAO
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
        flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")
        logging.exception("error with editing fm4")

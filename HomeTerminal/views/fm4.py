from datetime import datetime

from flask import (Blueprint, flash, render_template,
                   request)
from flask_login import login_required

from ..dao import (RowDoesNotExist, edit_fm4_item, get_fm4_categories,
                   get_fm4_expiring, get_fm4_item, get_fm4_report)
from ..models import FM4_Item
from ..utils import calc_expire_date

fm4 = Blueprint("fm4", __name__)

@fm4.route("/", methods=["GET", "POST"])
@login_required
def report():
    if request.method == "POST":
        category = request.form.get("category", "").capitalize()
        return render_template(
            "fm4/report.html",
            items=get_fm4_report(category),
            categories=get_fm4_categories())
    return render_template("fm4/report.html", categories=get_fm4_categories())

@fm4.route("/report-expiring", methods=["GET"])
@login_required
def report_expiring():
    items = get_fm4_expiring()
    return render_template("/fm4/report_expiring.html", items=items)

@fm4.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        try:
            id_ = int(request.form.get("id", -1))
            name = request.form["name"]
            amount = request.form["amount"]
            category = request.form["category"].capitalize()
            removed = request.form.get("removed", 0)
            if id_ == -1:
                id_ = None #TODO: handle this better (use empty string instead in form)
                if request.form.get("custom_expire", False) == "1":
                    expire = datetime.strptime(request.form["expire_date"], "%Y-%m-%d")
                else:
                    expire = calc_expire_date(request.form["expire"])
            edit_fm4_item(name, category, amount, expire, removed, id_)
            flash("Added Entry")
        except KeyError:
            flash("Missing required fields!", "warning")
        except RowDoesNotExist:
            flash("An item with that id does not exist!", "error")
    categories = get_fm4_categories()
    edit_item_id = request.args.get("item_id", default="", type=str)
    if edit_item_id == "":
        default_item = FM4_Item(name="", expire_date="", categoryname="", quantity=0, id_=-1)
    else:
        try:
            default_item = get_fm4_item(edit_item_id)
        except RowDoesNotExist:
            flash("An item with that id does not exist!", "error")
    return render_template("fm4/edit.html", categories=categories, def_item=default_item)

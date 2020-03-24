from datetime import datetime

from flask import Blueprint, flash, render_template, request
from flask_login import login_required

from ..database.dao.exceptions import RowDoesNotExist
from ..database.dao.freezer_manager import (edit_fm4_item, get_fm4_categories,
                                            get_fm4_expiring, get_fm4_item,
                                            get_fm4_report)
from ..database.models.freezer_manager import Item as FM_Item
from ..utils import calc_expire_date

fm = Blueprint("fm", __name__)

@fm.route("/", methods=["GET", "POST"])
@login_required
def report():
    if request.method == "POST":
        category = request.form.get("category", "").capitalize()
        return render_template(
            "freezer_manager/report.html",
            items=get_fm4_report(category),
            categories=get_fm4_categories())
    return render_template("freezer_manager/report.html", categories=get_fm4_categories())

@fm.route("/report-expiring", methods=["GET"])
@login_required
def report_expiring():
    items = get_fm4_expiring()
    return render_template("/freezer_manager/report_expiring.html", items=items)

@fm.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        try:
            id_ = request.form.get("id", None)
            name = request.form["name"]
            amount = request.form["amount"]
            category = request.form["category"].capitalize()
            removed = bool(request.form.get("removed", 0))
            expire = None
            if not id_:
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
        default_item = FM_Item(name="", expire_date="", category_id="", quantity=0, id_=None)
    else:
        try:
            default_item = get_fm4_item(edit_item_id)
        except RowDoesNotExist:
            flash("An item with that id does not exist!", "error")
    return render_template(
        "freezer_manager/edit.html",
        categories=categories, def_item=default_item)

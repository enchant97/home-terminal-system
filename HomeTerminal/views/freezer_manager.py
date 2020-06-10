from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ..database.dao.exceptions import RowDoesNotExist
from ..database.dao.freezer_manager import (edit_fm4_item, get_fm4_categories,
                                            get_fm4_expiring, get_fm4_item,
                                            get_fm4_report)
from ..database.models.freezer_manager import Item as FM_Item
from ..helpers.calculations import calc_expire_date

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

@fm.route("/edit/", defaults={"item_id": None}, methods=["GET", "POST"])
@fm.route("/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit(item_id):
    if request.method == "POST":
        try:
            name = request.form["name"]
            amount = request.form["amount"]
            category = request.form["category"].capitalize()
            removed = bool(request.form.get("removed", 0))
            expire = None
            if not item_id:
                if request.form.get("custom_expire", False) == "1":
                    expire = datetime.strptime(request.form["expire_date"], "%Y-%m-%d")
                else:
                    expire = calc_expire_date(request.form["expire"])
            edit_fm4_item(name, category, amount, expire, removed, item_id)
            flash("Added Entry")
            # return back to adding a new entry so the user cant edit the same item again
            return redirect(url_for(".edit"))
        except KeyError:
            flash("Missing required fields!", "warning")
        except RowDoesNotExist:
            flash("An item with that id does not exist!", "error")
    categories = get_fm4_categories()
    if not item_id:
        default_item = FM_Item(name="", expire_date="", category_id="", quantity=0, id_=None)
    else:
        try:
            default_item = get_fm4_item(item_id)
        except RowDoesNotExist:
            flash("An item with that id does not exist!", "error")
    return render_template(
        "freezer_manager/edit.html",
        categories=categories, def_item=default_item)

from flask import Blueprint, flash, render_template, request

from ..database.dao import inventory_manager as im_dao

im = Blueprint("im", __name__)

@im.route("/", methods=["GET", "POST"])
def view():
    items = ()
    if request.method == "POST":
        box_filter = request.form.get("box-filter", None)
        type_filter = request.form.get("type-filter", None)
        if box_filter and type_filter:
            items = im_dao.get_item(box_id=box_filter, type_id=type_filter)
        elif box_filter:
            items = im_dao.get_item(box_id=box_filter)
        elif type_filter:
            items = im_dao.get_item(type_id=type_filter)
        else:
            items = im_dao.get_item()
    boxes = im_dao.get_box()
    types = im_dao.get_type()
    return render_template("inventory_manager/view.html", items=items, boxes=boxes, types=types)

@im.route("/edit-box/", defaults={"box_id": None}, methods=["GET", "POST"])
@im.route("/edit-box/<box_id>", methods=["GET", "POST"])
def edit_box(box_id):
    if request.method == "POST":
        name = request.form["box-name"]
        loc_id = request.form["box-loc"]
        if box_id:
            #TODO: implement the edit of box
            flash("this is not implemented yet", "error")
        else:
            im_dao.new_box(loc_id, name)
            flash("added new box!")
    locs = im_dao.get_locations()
    if box_id:
        return render_template(
            "inventory_manager/edit-box.html",
            locations=locs, box=im_dao.get_box(first=True, id_=box_id))
    return render_template("inventory_manager/edit-box.html", locations=locs)

@im.route("/edit-item/", defaults={"item_id": None}, methods=["GET", "POST"])
@im.route("/edit-item/<item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    if request.method == "POST":
        name = request.form["item-name"]
        box_id = request.form["item-box"]
        type_id = request.form["item-type"]
        quantity = request.form["item-quantity"]
        in_box = request.form.get("item-inbox", False, bool)
        if item_id:
            #TODO: implement the edit of item
            flash("this is not implemented yet", "error")
        else:
            im_dao.new_item(name, box_id, quantity, type_id, in_box)
            flash("added new item!")
    boxes = im_dao.get_box()
    types = im_dao.get_type()
    if item_id:
        return render_template(
            "inventory_manager/edit-item.html", types=types,
            boxes=boxes, item=im_dao.get_item(first=True, id_=item_id))
    return render_template("inventory_manager/edit-item.html", types=types, boxes=boxes)

@im.route("/edit-type/", defaults={"type_id": None}, methods=["GET", "POST"])
@im.route("/edit-type/<type_id>", methods=["GET", "POST"])
def edit_type(type_id):
    if request.method == "POST":
        name = request.form["type-name"]
        if type_id:
            #TODO: implement the edit of item
            flash("this is not implemented yet", "error")
        else:
            im_dao.new_type(name)
            flash("added new item type!")
    if type_id:
        return render_template(
            "inventory_manager/edit-type.html",
            item_type=im_dao.get_type(first=True, id_=type_id))
    return render_template("inventory_manager/edit-type.html")

@im.route("/edit-location/", defaults={"location_id": None}, methods=["GET", "POST"])
@im.route("/edit-location/<location_id>", methods=["GET", "POST"])
def edit_location(location_id):
    if request.method == "POST":
        name = request.form["loc-name"]
        comment = request.form.get("loc-comment", None)
        if location_id:
            #TODO: implement the edit of location
            flash("this is not implemented yet", "error")
        else:
            im_dao.new_location(name, comment)
            flash("added new location!")
    if location_id:
        return render_template(
            "inventory_manager/edit-location.html",
            location=im_dao.get_locations(first=True, id_=location_id))
    return render_template("inventory_manager/edit-location.html")

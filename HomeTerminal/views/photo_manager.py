from datetime import datetime

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import login_required

from ..database.dao.exceptions import RowDoesNotExist
from ..database.dao.photo_manager import (edit_pd1_event, get_pd1_event, get_pd1_mainloc,
                                get_pd1_subloc)
from ..database.dao.user import get_users

pm = Blueprint("pm", __name__)

@pm.route("/report-subloc", methods=["GET"])
@login_required
def get_subloc():
    main_loc = request.args.get("mainloc", default="", type=str)
    sublocations = get_pd1_subloc(main_loc)
    if len(sublocations) > 0:
        return jsonify(main_loc=main_loc, sublocs=[subloc.serialize() for subloc in sublocations])
    return jsonify(sublocs=[])

@pm.route("/", methods=["GET", "POST"])
@login_required
def view():
    loaded_entries = ()
    filter_by = "(Please use display button to filter)"
    if request.method == "POST":
        mainloc = request.form.get("main-location").capitalize()
        subloc = request.form.get("sub-location").capitalize()
        if not mainloc:
            filter_by = "no filter"
            loaded_entries = get_pd1_event()
        elif mainloc and not subloc:
            filter_by = "main-loc"
            #loaded_entries = get_pd1_event(mainloc)
            flash("Searching just by mainloc not supported yet :(", "error")
        else:
            filter_by = "sub-loc"
            try:
                loaded_entries = get_pd1_event(mainloc, subloc)
            except RowDoesNotExist:
                flash(f"sub location '{subloc}' does not exist", "error")
    main_locations = get_pd1_mainloc()
    return render_template(
        "/photo_manager/view.html", main_locations=main_locations,
        loaded_entries=loaded_entries, filter_by=filter_by)

@pm.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        try:
            mainloc = request.form["mainloc"].capitalize()
            subloc = request.form["subloc"].capitalize()
            datetaken = datetime.strptime(request.form["datetaken"], "%Y-%m-%d")
            notes = request.form["notes"]
            users = request.form.getlist("user", type=str)

            lat = request.form.get("lat", 0, int)
            lng = request.form.get("lng", 0, int)

            if users:
                edit_pd1_event(mainloc, subloc, datetaken, notes, users, lat, lng)
                flash("added entry")
            else:
                flash("not added as no users were selected", "warning")
        except KeyError:
            flash("Missing required fields!", "error")
    main_locations = get_pd1_mainloc()
    return render_template("photo_manager/edit.html", main_locations=main_locations, users=get_users())

#TODO: make a new function allowing for new location to be added

import os
from datetime import datetime

from flask import (Blueprint, abort, current_app, flash, jsonify, redirect,
                   render_template, request, send_file, url_for)
from flask_login import login_required

from ..database.dao import photo_manager as dao_pm
from ..database.dao.exceptions import RowDoesNotExist
from ..database.dao.user import get_users
from ..helpers.paths import is_allowed_img_file
from ..helpers.photos import compress_jpg_thumbnail

pm = Blueprint("pm", __name__)

@pm.route("/report-subloc", methods=["GET"])
@login_required
def get_subloc():
    main_loc = request.args.get("mainloc", default="", type=str)
    sublocations = dao_pm.get_subloc(main_loc)
    if len(sublocations) > 0:
        return jsonify(main_loc=main_loc, sublocs=[subloc.serialize() for subloc in sublocations])
    return jsonify(sublocs=[])

@pm.route("/thumbnails/<int:event_id>.jpg")
@login_required
def thumbnail(event_id):
    file_path = dao_pm.get_image_by_event(event_id)
    if file_path:
        full_path = os.path.join(current_app.config["IMG_LOCATION"], file_path.file_path)
        return send_file(full_path)
    return abort(404)

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
            loaded_entries = dao_pm.get_event()
        elif mainloc and not subloc:
            filter_by = "main-loc"
            #loaded_entries = get_pd1_event(mainloc)
            flash("Searching just by mainloc not supported yet :(", "error")
        else:
            filter_by = "sub-loc"
            try:
                loaded_entries = dao_pm.get_event(mainloc, subloc)
            except RowDoesNotExist:
                flash(f"sub location '{subloc}' does not exist", "error")
    main_locations = dao_pm.get_mainloc()
    return render_template(
        "/photo_manager/view.html", main_locations=main_locations,
        loaded_entries=loaded_entries, filter_by=filter_by)

@pm.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        try:
            mainloc = request.form["mainloc"].capitalize()
            subloc = request.form["subloc"].capitalize()
            datetaken = datetime.strptime(request.form["datetaken"], "%Y-%m-%d")
            notes = request.form["notes"]
            users = request.form.getlist("user", type=str)
            picture = request.files.get("pic", None)

            lat = request.form.get("lat", 0, int)
            lng = request.form.get("lng", 0, int)

            if users:
                if picture and current_app.config.get("IMG_LOCATION"):
                    if is_allowed_img_file(picture.filename):
                        bytes_picture = compress_jpg_thumbnail(
                            picture,
                            current_app.config["MAX_IMAGE_SIZE"],
                            current_app.config["JPEG_QUALITY"])
                    else:
                        flash("image is not in allowed format", "error")
                        return redirect(url_for(".new"))
                else:
                    bytes_picture = None
                dao_pm.new_event(mainloc, subloc, datetaken, notes, users, lat, lng, bytes_picture)
                flash("added entry")
            else:
                flash("not added as no users were selected", "warning")
        except KeyError:
            flash("Missing required fields!", "error")
    main_locations = dao_pm.get_mainloc()
    users = get_users()
    return render_template("photo_manager/new.html", main_locations=main_locations, users=users)

#TODO: make a new function allowing for new location to be added

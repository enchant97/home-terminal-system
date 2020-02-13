import logging
from datetime import datetime

from flask import (Blueprint, current_app, flash, jsonify, render_template,
                   request, url_for)
from flask_login import login_required

from ..models import (PD1_FullEvent, PD1_MainLocation, PD1_SubLocation,
                      PD1_UserEvent, User, db)

pd1 = Blueprint("pd1", __name__)

@pd1.route("/report-subloc", methods=["GET"])
@login_required
def get_pd1_subloc():
    #TODO: seperate into DAO
    main_loc = request.args.get("mainloc", default="", type=str)
    sublocations = PD1_SubLocation.query.filter_by(main_name=main_loc).all()
    if len(sublocations) > 0:
        return jsonify(main_loc=main_loc, sublocs=[subloc.serialize() for subloc in sublocations])
    return jsonify(sublocs=[])

@pd1.route("/", methods=["GET", "POST"])
@login_required
def pd1_view():
    #TODO: seperate into DAO
    loaded_entries = ()
    filter_by = "no filter"
    try:
        if request.method == "POST":
                mainloc = request.form.get("main-location", "", str).capitalize()
                subloc = request.form.get("sub-location", "", str).capitalize()
                if mainloc == "":
                    loaded_entries = PD1_FullEvent.query.all()
                elif mainloc != "" and subloc == "":
                    # TODO: allow for user wanting all sub locations
                    filter_by = "main-loc"
                    pass
                else:
                    filter_by = "sub-loc"
                    if PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).scalar():
                        subloc = PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).first()
                        loaded_entries = PD1_FullEvent.query.filter_by(subloc=subloc.id_).all()
                    else:
                        loaded_entries = ()
        else:
            # if user is just loading the page use default, show-none
            filter_by = "(Please use display button to filter)"
    except:
        logging.exception("error viewing pd1")
        flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")
    main_locations = PD1_MainLocation.query.order_by(PD1_MainLocation.name).all()
    return render_template("/pd1/view.html", main_locations=main_locations, loaded_entries=loaded_entries, filter_by=filter_by)

@pd1.route("/edit", methods=["GET", "POST"])
@login_required
def get_pd1_edit():
    #TODO: seperate into DAO
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
                if not PD1_MainLocation.query.filter_by(name=mainloc).scalar():
                    # add main location if it does not exist
                    db.session.add(PD1_MainLocation(name=mainloc))
                    db.session.commit()
                if not PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).scalar():
                    # add sub location if it does not exist
                    subloc = PD1_SubLocation(name=subloc, main_name=mainloc, lat=lat, lng=lng)
                    db.session.add(subloc)
                    db.session.commit()
                else:
                    subloc = PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).first()
                fullevent = PD1_FullEvent(subloc=subloc.id_, date_taken=datetaken, notes=notes)
                db.session.add(fullevent)
                db.session.commit()
                for user in users:
                    # adds all the user events by selected user
                    db.session.add(PD1_UserEvent(full_event=fullevent.id_, username=user.lower()))
                db.session.commit()
                flash("added entry")
            else:
                flash("not added as no users were selected", "warning")
        except:
            logging.exception("error adding pd1 entry")
            flash(current_app.config["SERVER_ERROR_MESSAGE"], "error")
    main_locations = PD1_MainLocation.query.order_by(PD1_MainLocation.name).all()
    return render_template("pd1/edit.html", main_locations=main_locations, users=User.query.filter_by(removed=0).all())

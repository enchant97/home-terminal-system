"""
functions for abstracting the photo database models
"""
import os
from datetime import datetime

from flask import current_app

from ..database import db
from ..models.photo_manager import (FullEvent, MainLocation, SubLocation,
                                    Thumbnail, UserEvent)
from ..models.user import User
from .exceptions import RowDoesNotExist
from ...utils import get_hash_image

def get_subloc(main_loc):
    """
    returns the sublocations related to the main_loc given
    """
    main = MainLocation.query.filter_by(name=main_loc).first()
    if main_loc:
        return SubLocation.query.filter_by(main_loc_id=main.id_).all()
    raise RowDoesNotExist(f"mainlocation {main_loc} does not exist")

def get_mainloc():
    """
    returns PD1_MainLocation objects,
    ordered by mainlocation name
    """
    return MainLocation.query.order_by(MainLocation.name).all()

def get_image_by_event(event_id, removed=False):
    """
    returns the Thumbnail obj
    """
    return Thumbnail.query.filter_by(full_event_id=event_id, removed=removed).first()

def get_event(mainloc=None, subloc=None):
    """
    returns PD1_FullEvent objects

    args:
        mainloc : used to filter by main location
        subloc : used to filter by sub location
    """
    if not mainloc and not subloc:
        # select all (no-filter)
        return FullEvent.query.all()
    if mainloc and not subloc:
        #TODO: implement search by mainloc
        raise NotImplementedError("filter by mainloc not implemented")
    if mainloc and subloc:
        main_loc = MainLocation.query.filter_by(name=mainloc).first()
        if main_loc:
            subloc = SubLocation.query.filter_by(name=subloc, main_loc_id=main_loc.id_).first()
            if subloc:
                return FullEvent.query.filter_by(subloc_id=subloc.id_).all()
            raise RowDoesNotExist("sub location does not exist")
        else:
            raise RowDoesNotExist(f"main location name {mainloc} does not exist")
    raise Exception("Not a supported filter")

def new_event(mainloc, subloc, datetaken: datetime, notes, users, lat, lng, img_raw=None):
    """
    Allows for adding a new PD1_FullEvent,
    returns PD1_FullEvent obj

    args:
        mainloc:
        subloc:
        datetaken:
        notes:
        users: list/tuple of usernames
        lat:
        lng:
        img_raw : io.BytesIO object for the image file
    """

    # get or create then get mainlocation
    if not MainLocation.query.filter_by(name=mainloc).scalar():
        # add main location if it does not exist
        main_loc = MainLocation(name=mainloc)
        db.session.add(main_loc)
        db.session.commit()
    else:
        main_loc = MainLocation.query.filter_by(name=mainloc).first()


    # get or create then get sublocation
    if not SubLocation.query.filter_by(name=subloc, main_loc_id=main_loc.id_).scalar():
        # add sub location if it does not exist
        subloc = SubLocation(name=subloc, main_loc_id=main_loc.id_, lat=lat, lng=lng)
        db.session.add(subloc)
        db.session.commit()
    else:
        subloc = SubLocation.query.filter_by(name=subloc, main_loc_id=main_loc.id_).first()
    fullevent = FullEvent(subloc_id=subloc.id_, date_taken=datetaken, notes=notes)
    db.session.add(fullevent)
    db.session.commit()
    if img_raw:
        # if a img_path was provided add it to the database and write image to file
        full_path = get_hash_image(img_raw.read(), ".jpg", current_app.config["IMG_LOCATION"])
        img_raw.seek(0)# go back to start of file
        with open(full_path, "wb") as fo:
            fo.write(img_raw.read())
        img_raw.close()# close the image (allows garbage cleanup to remove)
        filename = os.path.basename(full_path)
        db.session.add(Thumbnail(full_event_id=fullevent.id_, file_path=filename))
    for username in users:
        # adds all the user events by selected user
        the_user = User.query.filter_by(username=username).first()
        if not the_user:
            raise RowDoesNotExist(f"username {username} does not exist")
        db.session.add(UserEvent(full_event_id=fullevent.id_, user_id=the_user.id_))
    db.session.commit()

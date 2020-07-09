"""
functions for abstracting the photo database models
"""
from datetime import datetime

from ...helpers.paths import get_image_folder
from ...helpers.photos import get_hash_image
from ..database import db
from ..models.photo_manager import (FullEvent, MainLocation, SubLocation,
                                    Thumbnail, UserEvent)
from ..models.user import User
from .exceptions import RowDoesNotExist


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
        raise RowDoesNotExist(f"main location name {mainloc} does not exist")
    raise Exception("Not a supported filter")

def new_event(mainloc, subloc, datetaken: datetime, notes, users, img_raw=None):
    """
    Allows for adding a new PD1_FullEvent,
    returns PD1_FullEvent obj

    args:
        mainloc:
        subloc:
        datetaken:
        notes:
        users: list/tuple of usernames
        img_raw : io.BytesIO object for the image file
    """

    main_loc = MainLocation.query.filter_by(name=mainloc).first()
    if not main_loc:
        raise RowDoesNotExist(f"main location {mainloc} does not exist")

    sub_loc = SubLocation.query.filter_by(name=subloc, main_loc_id=main_loc.id_).first()
    if not sub_loc:
        raise RowDoesNotExist(f"sub location {subloc} does not exist")

    fullevent = FullEvent(subloc_id=sub_loc.id_, date_taken=datetaken, notes=notes)
    db.session.add(fullevent)
    db.session.commit()
    if img_raw:
        # if a img_path was provided add it to the database and write image to file
        file_name = get_hash_image(img_raw.read(), ".jpg")
        full_path = get_image_folder("PHOTO_MANAGER") / file_name
        img_raw.seek(0)# go back to start of file
        full_path.write_bytes(img_raw.read())
        img_raw.close()# close the image (allows garbage cleanup to remove)
        db.session.add(Thumbnail(full_event_id=fullevent.id_, file_path=file_name))
    for username in users:
        # adds all the user events by selected user
        the_user = User.query.filter_by(username=username).first()
        if not the_user:
            raise RowDoesNotExist(f"username {username} does not exist")
        db.session.add(UserEvent(full_event_id=fullevent.id_, user_id=the_user.id_))
    db.session.commit()
    return fullevent

def new_subloc(sub_loc_name, lat, lng, main_loc_name, removed=False):
    """
    allow for a new sub location to be added

        :param sub_loc_name: the sub location name
        :param lat: the sub locations latitude
        :param lng: the sub locations longitude
        :param main_loc_name: the main locations name
        :param removed: whether it is removed
        :return: the added sublocation
        :rtype: SubLocation
    """
    main_loc = MainLocation.query.filter_by(name=main_loc_name).first()
    if not main_loc:
        main_loc = MainLocation(name=main_loc)
        db.session.add(main_loc)
        db.session.commit()

    sub_loc = SubLocation(
        name=sub_loc_name,
        main_loc_id=main_loc.id_,
        lat=lat,
        lng=lng,
        removed=removed
    )

    db.session.add(sub_loc)
    db.session.commit()

    return sub_loc

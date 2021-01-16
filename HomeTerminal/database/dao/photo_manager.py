"""
functions for abstracting the photo database models
"""
from datetime import datetime

from ...helpers.paths import get_image_folder
from ...helpers.photos import get_hash_image
from ..database import db
from ..models.photo_manager import (FullEvent, MainLocation, SubLocation,
                                    UserEvent)
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

def get_thumbnail_fn(event_id: int):
    """
    returns the thumbnail filename if exists

        :param event_id: the full event id
        :return: the thumbnail filename or None
    """
    event = FullEvent.query.filter_by(id_=event_id, removed=False).first()
    if event:
        return event.thumbnail_filename
    return None

def get_event(mainloc=None, subloc=None, sort_dated: bool = None):
    """
    returns FullEvent objects

        :param mainloc: used to filter by main location
        :param subloc: used to filter by sub location
        :param sort_dated: used to either sort the date
                in ascending(True) or descending(False) order
        :return: FullEvent objects from database
        :rtype: FullEvent
    """
    if not mainloc and not subloc:
        # select all (no-filter)
        events = FullEvent.query

    elif mainloc:
        main_loc = MainLocation.query.filter_by(name=mainloc).first()
        if not main_loc:
            raise RowDoesNotExist(f"main location name {mainloc} does not exist")

        if subloc:
            # if mainloc and subloc are given
            subloc = SubLocation.query.filter_by(name=subloc, main_loc_id=main_loc.id_).first()
            if subloc:
                events = FullEvent.query.filter_by(subloc_id=subloc.id_)
            raise RowDoesNotExist("sub location does not exist")
        # if just mainloc was specified
        events = FullEvent.query.filter(FullEvent.sub_location.has(main_loc_id=main_loc.id_))
    else:
        raise Exception("Not a supported filter")

    # whether to sort the entries
    if sort_dated is not None:
        if sort_dated is True:
            events = events.order_by(FullEvent.date_taken.asc())
        elif sort_dated is False:
            events = events.order_by(FullEvent.date_taken.desc())
        else:
            raise ValueError("sort_dated must be None or True/False")
    events.all()
    return events

def new_event(mainloc, subloc, datetaken: datetime, notes, users, img_raw=None):
    """
    Allows for adding a new PD1_FullEvent,
    returns PD1_FullEvent obj

        :param mainloc: the mainloc name
        :param subloc: the subloc name
        :param datetaken: datetime that it was taken
        :param notes: the notes
        :param users: list/tuple of usernames
        :param img_raw : io.BytesIO object for the image file
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
        #TODO move image write into a helper func
        file_name = get_hash_image(img_raw.read(), ".jpg")
        full_path = get_image_folder("PHOTO_MANAGER") / file_name
        img_raw.seek(0)# go back to start of file
        full_path.write_bytes(img_raw.read())
        img_raw.close()# close the image (allows garbage cleanup to remove)
        fullevent.thumbnail_filename = file_name
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
        main_loc = MainLocation(name=main_loc_name)
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

def delete_removed():
    """
    delete the rows that are marked as removed
    """
    UserEvent.query.filter_by(removed=True).delete()
    FullEvent.query.filter_by(removed=True).delete()
    SubLocation.query.filter_by(removed=True).delete()
    MainLocation.query.filter_by(removed=True).delete()
    db.session.commit()

from datetime import datetime

from ..database import db
from ..models.pd1 import (PD1_FullEvent, PD1_MainLocation, PD1_SubLocation,
                          PD1_UserEvent)
from .exceptions import RowDoesNotExist


def get_pd1_subloc(main_loc):
    """
    returns the sublocations related to the main_loc given
    """
    return PD1_SubLocation.query.filter_by(main_name=main_loc).all()

def get_pd1_mainloc():
    """
    returns PD1_MainLocation objects,
    ordered by mainlocation name
    """
    return PD1_MainLocation.query.order_by(PD1_MainLocation.name).all()

def get_pd1_event(mainloc=None, subloc=None):
    """
    returns PD1_FullEvent objects

    args:
        mainloc : used to filter by main location
        subloc : used to filter by sub location
    """
    if not mainloc and not subloc:
        # select all (no-filter)
        return PD1_FullEvent.query.all()
    if mainloc and not subloc:
        #TODO: implement search by mainloc
        raise NotImplementedError("filter by mainloc not implemented")
    if mainloc and subloc:
        subloc = PD1_SubLocation.query.filter_by(name=subloc, main_name=mainloc).first()
        if subloc:
            return PD1_FullEvent.query.filter_by(subloc=subloc.id_).all()
        raise RowDoesNotExist("sub location does not exist")
    raise Exception("Not a supported filter")

def edit_pd1_event(mainloc, subloc, datetaken: datetime, notes, users, lat, lng, id_=None):
    """
    Allows for editing or adding a new PD1_FullEvent,
    editing is not implemented,
    returns PD1_FullEvent obj

    args:
        mainloc:
        subloc:
        datetaken:
        notes:
        users: list/tuple of usernames
        lat:
        lng:
        id_: id of the full event if editing
    """
    if id_:
        #TODO: implement
        raise NotImplementedError("edit fullevent not available :(")
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

from ..database import db


class PD1_SubLocation(db.Model):
    """
    Where the sub location data is stored
    """
    __tablename__ = "pd1_subloc"
    id_ = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(length=500), nullable=False)
    main_name = db.Column(
        "main_name", db.String(length=500),
        db.ForeignKey("pd1_mainloc.name"), nullable=False)
    lat = db.Column("lat", db.Float(precision=10, decimal_return_scale=None), nullable=False)
    lng = db.Column("lng", db.Float(precision=10, decimal_return_scale=None), nullable=False)

    def serialize(self):
        return {
            "name":self.name,
            "main_name":self.main_name
        }

class PD1_FullEvent(db.Model):
    """
    Where the full event data is stored
    """
    __tablename__ = "pd1_fullevent"
    id_ = db.Column("id", db.Integer, primary_key=True)
    subloc = db.Column("subloc_id", db.Integer, db.ForeignKey("pd1_subloc.id"), nullable=False)
    date_taken = db.Column("datetaken", db.DateTime, nullable=False)
    notes = db.Column("notes", db.String(length=2000), nullable=False)

class PD1_UserEvent(db.Model):
    """
    Where the user event data is stored
    """
    __tablename__ = "pd1_userevent"
    id_ = db.Column("id", db.Integer, primary_key=True)
    full_event = db.Column(
        "fullevent", db.Integer,
        db.ForeignKey("pd1_fullevent.id"), nullable=False)
    username = db.Column(
        "username", db.String(length=80),
        db.ForeignKey("user.username"), nullable=False)

class PD1_MainLocation(db.Model):
    """
    Where the main location data is stored
    """
    __tablename__ = "pd1_mainloc"
    name = db.Column("name", db.String(length=500), primary_key=True)

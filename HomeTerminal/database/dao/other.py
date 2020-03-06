from datetime import datetime

from ..database import db
from ..models.other import Table_Updates


def mark_table_updated(table_name):
    """
    Change a the update time table row,
    uses utc time

    args:
        just_creating : if the row already exists will not update the datetime
    """
    if Table_Updates.query.filter_by(table_name=table_name).scalar():
        new_row = Table_Updates.query.filter_by(table_name=table_name)
        new_row.last_updated = datetime.utcnow()
    else:
        new_row = Table_Updates(table_name=table_name)
    db.session.add(new_row)
    db.session.commit()

def get_last_updated(table_name):
    """
    Returns the last time the table was updated,
    returns a datetime obj
    """
    sel_row = Table_Updates.query.filter_by(table_name=table_name).first()
    if sel_row:
        return sel_row.last_updated

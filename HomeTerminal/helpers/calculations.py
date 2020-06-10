"""
functions that perform some kind of calculation
"""

import datetime
from functools import lru_cache


@lru_cache(maxsize=15)
def calc_expire_date(months: int) -> datetime.datetime:
    """
    Returns date
    excepts months betweeen 0-12

        :param months: the months to calculate

    .. todo:: #TODO find a better way of handling this
    """
    try:
        months = int(months)
    except ValueError:
        months = 0

    if months == 0:
        days = 7
    elif months == 1:
        days = 30
    elif months == 2:
        days = 60
    elif months == 3:
        days = 91
    elif months == 4:
        days = 121
    elif months == 5:
        days = 152
    elif months == 6:
        days = 182
    elif months == 7:
        days = 212
    elif months == 8:
        days = 243
    elif months == 9:
        days = 273
    elif months == 10:
        days = 304
    elif months == 11:
        days = 334
    elif months == 12:
        days = 365
    else:
        return None
    return datetime.datetime.now() + datetime.timedelta(days=days)

"""
functions that perform some kind of calculation
"""

from calendar import monthrange
from datetime import datetime
from functools import lru_cache


@lru_cache(maxsize=15)
def calc_expire_date(months: int, start_dt: datetime = None) -> datetime:
    """
    calculates the date from current
    date incremented by given months

        :param months: the months to increment by
        :param start_dt: the datetime to increment will use datetime.now() if None
        :rtype: datetime.datetime

    ..todo:: #TODO rename this function later to add_months
    """
    months = int(months)

    if not start_dt:
        start_dt = datetime.now()

    month = start_dt.month - 1 + months
    year = start_dt.year + month // 12
    month = month % 12 + 1
    day = min(start_dt.day, monthrange(year, month)[1])
    return datetime(
        year, month, day, start_dt.hour, start_dt.minute,
        start_dt.second, start_dt.microsecond, start_dt.tzinfo
        )

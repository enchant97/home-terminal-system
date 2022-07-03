"""
functions that perform some kind of calculation
"""

from calendar import monthrange
from datetime import datetime


def add_months(months: int, start_dt: datetime | None = None) -> datetime:
    """
    calculates the date from current
    date incremented by given months

        :param months: the months to increment by
        :param start_dt: the datetime to increment will use datetime.now() if None
        :rtype: datetime.datetime
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


def to_human_datetime(dt: datetime, show_date=True, show_time=False, ignore_none=True) -> str:
    """
    returns a 'human readable' format of the date or time or both

        :param dt: the input datetime obj to convert
        :param show_date: whether to include the date, defaults to True
        :param show_time: whether to include the time, defaults to False
        :param ignore_none: return N/A if dt is None, defaults to True
    """
    if ignore_none and not dt:
        return "N/A"
    if not show_date and not show_time:
        raise ValueError("Both show_date and show_time cannot be False")

    if show_date and show_time:
        return datetime.strftime(dt, "%d-%m-%Y %H:%M")

    if show_date:
        return datetime.strftime(dt, "%d-%m-%Y")

    return datetime.strftime(dt, "%H:%M")


def html_date(date_str: str) -> datetime:
    """
    used in a flask request.form.get as
    a type arg for a html date picker

        :param date_str: the date as a string as "%Y-%m-%d"
        :raises ValueError: if date can't be converted
        :return: the converted date into a datetime obj
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except TypeError as e:
        raise ValueError("Not a valid date value, must be: %Y-%m-%d") from e

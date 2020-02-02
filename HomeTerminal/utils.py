"""
Small functions which do useful things
"""
import hashlib
import datetime
from functools import lru_cache

def hash_str(str_to_hash):
    """returns a hashed version of the string in sha512"""
    return hashlib.sha512(str_to_hash.encode()).hexdigest()

@lru_cache(maxsize=15)
def calc_expire_date(months):
    """
    Returns date
    excepts months betweeen 0-12
    """
    try:
        months = int(months)
    except:
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

class Notification:
    """
    used to store each notfication for the user
    """
    def __init__(self, content, category="message"):
        self.content = content
        self.category = category

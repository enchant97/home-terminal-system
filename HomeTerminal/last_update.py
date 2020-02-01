from datetime import datetime

class LastUpdate:
    __last_update = None
    def update_now(self):
        """
        updates the last_update time to current utc time
        """
        self.__last_update = datetime.utcnow()
    
    def is_uptodate(self, compare_date):
        """
        returns whether the datetime given is more recent or equal
        """
        if compare_date >= self.__last_update:
            return True
        return False

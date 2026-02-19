all = ['DTFormat']

from datetime import\
    datetime as _datetime

class DTFormat:
    """
    Represents a date/time format
    """

    #region init

    def __init__(self, dformat:str, time12:bool):
        """
        Initializer for DTFormat

        :param dformat:
            Date format (ex: MM/DD/YY, DD/MM/YYYY, YY/MM/DD)
        :param time12:
            Whether or not the display time in 12-hour format
        """
        self.__date = dformat.\
            replace("{", "{{").\
            replace("}", "}}").\
            replace("YYYY", "{0:04}").\
            replace("YY", "{1:02}").\
            replace("MM", "{2:02}").\
            replace("DD", "{3:02}")
        self.__time12 = time12

    #endregion

    #region methods

    def create(self, dt:_datetime):
        """
        Creates a string representation of the specified date/time
        """
        # Create string representation of date
        datestr = self.__date.format(\
            dt.year, dt.year % 100, dt.month, dt.day)
        # Create string representation of time
        if self.__time12:
            _hour = 12 if (dt.hour == 0) else (dt.hour % 12)
            _ampm = "PM" if (dt.hour >= 12) else "AM"
            timestr = f"{_hour:02}:{dt.minute:02}:{dt.second:02} {_ampm}"
        else:
            timestr = f"{dt.hour:02}:{dt.minute:02}:{dt.second:02}"
        # Create final string representation
        return f"{datestr} {timestr}"

    #endregion
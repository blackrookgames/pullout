all = ['DTUtil']

from collections.abc import\
    Iterable as _Iterable
from datetime import\
    datetime as _datetime

class DTUtil:
    """
    Utility for operations related to date/time
    """

    #region helper methods

    @staticmethod
    def __presum(iter:_Iterable[int]):
        sums:list[int] = []
        _sum = 0
        for _item in iter:
            _sum += _item
            sums.append(_sum)
        return tuple[int](sums)

    @staticmethod
    def __postsum(iter:_Iterable[int]):
        sums:list[int] = []
        _sum = 0
        for _item in iter:
            sums.append(_sum)
            _sum += _item
        return tuple[int](sums)

    #endregion

    #region const

    LPYRS_100YRS = 24
    """
    Number of leap years in 100 years, assuming the first year is a centurial year that's not divisible by 400
    """

    LPYRS_400YRS = LPYRS_100YRS * 4 + 1
    """
    Number of leap years in 400 years, assuming the first year is a centurial year that's divisible by 400
    """

    MICRO_SEC = 1000000
    """
    Number of microseconds in a second
    """

    MICRO_MIN = MICRO_SEC * 60
    """
    Number of microseconds in a minute
    """

    MICRO_HR = MICRO_MIN * 60
    """
    Number of microseconds in an hour
    """

    MICRO_DAY = MICRO_HR * 24
    """
    Number of microseconds in a day
    """

    MICRO_CMYR = MICRO_DAY * 365
    """
    Number of microseconds in a common (365 days) year
    """

    MICRO_LPYR = MICRO_CMYR + MICRO_DAY
    """
    Number of microseconds in a leap (366 days) year
    """

    MICRO_100YRS = MICRO_CMYR * (100 - LPYRS_100YRS) + MICRO_LPYR * LPYRS_100YRS
    """
    Number of microseconds in 100 years, assuming the first year is a centurial year that's not divisible by 400
    """

    MICRO_400YRS = MICRO_100YRS * 4 + MICRO_DAY
    """
    Number of microseconds in 400 years, assuming the first year is a centurial year that's divisible by 400
    """

    DAYS_CMYR = 365
    """
    Number of days in a common year
    """

    DAYS_LPYR = 366
    """
    Number of days in a leap year
    """

    DAYS_100YRS = DAYS_CMYR * (100 - LPYRS_100YRS) + DAYS_LPYR * LPYRS_100YRS
    """
    Number of days in 100 years, assuming the first year is a centurial year that's not divisible by 400
    """

    DAYS_400YRS = DAYS_100YRS * 4 + 1
    """
    Number of days in 400 years, assuming the first year is a centurial year that's divisible by 400
    """

    #endregion

    #region helper const

    __MONTHS_CMDAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    __MONTHS_LPDAYS = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    __MONTHS_MICRO = __postsum([\
        MICRO_DAY * 31,\
        MICRO_DAY * 28,\
        MICRO_DAY * 31,\
        MICRO_DAY * 30,\
        MICRO_DAY * 31,\
        MICRO_DAY * 30,\
        MICRO_DAY * 31,\
        MICRO_DAY * 31,\
        MICRO_DAY * 30,\
        MICRO_DAY * 31,\
        MICRO_DAY * 30,\
        MICRO_DAY * 31])

    #endregion

    @classmethod
    def from_micro2000(cls, microseconds:int):
        """
        Computes the date/time using the specified number of microseconds since Jan 1, 2000 12:00:00.000000 AM
        
        :param microseconds:
            Microseconds since Jan 1, 2000 12:00:00.000000 AM (must be >= 0)
        :return:
            Computed date/time
        :raise ValueError:
            microseconds is less than zero
        """
        if microseconds < 0:
            raise ValueError("microseconds must be greater than or equal to zero.")
        value = microseconds
        # Microseconds
        dt_microseconds = value % 1000000
        value //= 1000000
        # Seconds
        dt_seconds = value % 60
        value //= 60
        # Minute
        dt_minute = value % 60
        value //= 60
        # Hour
        dt_hour = value % 24
        value //= 24
        # Year
        dt_year = 2000 + (value // cls.DAYS_400YRS) * 400
        value %= cls.DAYS_400YRS
        islpyr = False
        while True:
            islpyr = (dt_year % 4) == 0 and ((dt_year % 100) != 0 or (dt_year % 400) == 0)
            _days = 366 if islpyr else 365
            if value < _days: break
            value -= _days
            dt_year += 1
        # Month
        _months_days = cls.__MONTHS_LPDAYS if islpyr else cls.__MONTHS_CMDAYS
        dt_month = 0
        while value >= _months_days[dt_month]:
            value -= _months_days[dt_month]
            dt_month += 1
        dt_month += 1
        # Day
        dt_day = value + 1
        # Success!!!
        return _datetime(dt_year, dt_month, dt_day, dt_hour, dt_minute, dt_seconds, dt_microseconds)

    @classmethod
    def to_micro2000(cls, dt:_datetime):
        """
        Computes the number of microseconds since Jan 1, 2000 12:00:00.000000 AM
        
        :param dt:
            Date/time (must be at or after Jan 1, 2000 12:00:00.000000 AM)
        :return:
            Difference in microseconds
        :raise ValueError:
            dt comes before Jan 1, 2000 12:00:00.000000 AM
        """
        if dt.year < 2000:
            raise ValueError("dt cannot be before Jan 1, 2000 12:00:00.000000 AM.")
        microseconds = 0
        # Year
        year = dt.year - 2000
        islpyr = (year % 4) == 0 and ((year % 100) != 0 or (year % 400) == 0)
        lpyrs = ((year + 399) // 400) + (year // 100) * cls.LPYRS_100YRS
        if (year % 100) >= 1: lpyrs += ((year % 100) - 1) // 4
        microseconds += year * cls.MICRO_CMYR + lpyrs * cls.MICRO_DAY
        # Month
        microseconds += cls.__MONTHS_MICRO[dt.month - 1]
        if islpyr and dt.month > 2: microseconds += cls.MICRO_DAY 
        # Day
        microseconds += (dt.day - 1) * cls.MICRO_DAY
        # Hour
        microseconds += dt.hour * cls.MICRO_HR
        # Minute
        microseconds += dt.minute * cls.MICRO_MIN
        # Seconds
        microseconds += dt.second * cls.MICRO_SEC
        # Microseconds
        microseconds += dt.microsecond
        # Success!!!
        return microseconds
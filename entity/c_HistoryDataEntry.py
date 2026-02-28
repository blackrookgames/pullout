all = ['HistoryDataEntry']

from datetime import\
    datetime as _datetime

class HistoryDataEntry:
    """
    Represents a history data entry
    """

    #region init

    def __init__(self, dt:_datetime, price:float):
        """
        Initializer for HistoryDataEntry

        :params dt:
            Date/time
        :params price:
            Price
        """
        super().__init__()
        self.__dt = dt
        self.__price = price

    #endregion

    #region properties

    @property
    def dt(self):
        """
        Date/time
        """
        return self.__dt

    @property
    def price(self):
        """
        Price
        """
        return self.__price

    #endregion
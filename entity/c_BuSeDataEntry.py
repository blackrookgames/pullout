all = ['BuSeDataEntry']

class BuSeDataEntry:
    """
    Represents a price history used for buying/selling
    """

    #region init

    def __init__(self, price:float):
        """
        Initializer for BuSeDataEntry

        :params price:
            Price
        """
        super().__init__()
        self.__price = price

    #endregion

    #region properties

    @property
    def price(self):
        """
        Price
        """
        return self.__price

    #endregion
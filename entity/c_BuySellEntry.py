all = ['BuySellEntry']

class BuySellEntry:
    """
    Represents an entry within a buy/sell object
    """

    #region init

    def __init__(self, name:str):
        """
        Initializer for BuySellEntry

        :params name:
            Name of crypto
        """
        super().__init__()
        self.__name = name
        self.__price = 0.0
        self.__investing = False
        self.__balance = 0.0
        self.__noncrypto = 0.0
        self.__priceinc:None|float = None
        self.__compromised = False

    #endregion

    #region properties

    @property
    def name(self):
        """
        Crypto name
        """
        return self.__name

    @property
    def price(self):
        """
        Crypto price
        """
        return self.__price
    @price.setter
    def price(self, value:float):
        self.__price = value

    @property
    def investing(self):
        """
        Whether or not investing in crypto
        """
        return self.__investing
    @investing.setter
    def investing(self, value:bool):
        self.__investing = value

    @property
    def balance(self):
        """
        Crypto balance
        """
        return self.__balance
    @balance.setter
    def balance(self, value:float):
        self.__balance = value
    
    @property
    def noncrypto(self):
        """
        Fraction of non-crypto to use for buying crypto
        """
        return self.__noncrypto
    @noncrypto.setter
    def noncrypto(self, value:float):
        self.__noncrypto = value
    
    @property
    def priceinc(self):
        """
        Increase (or decrease) in price
        """
        return self.__priceinc
    @priceinc.setter
    def priceinc(self, value:None|float):
        self.__priceinc = value

    @property
    def compromised(self):
        """
        Whether or not integrity has been compromised
        """
        return self.__compromised
    @compromised.setter
    def compromised(self, value:bool):
        self.__compromised = value

    #endregion
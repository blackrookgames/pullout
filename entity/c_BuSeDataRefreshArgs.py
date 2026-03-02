all = ['BuSeDataRefreshArgs']

from .c_BuSeDataFunc import\
    func_buy as _func_buy,\
    func_sell as _func_sell

class BuSeDataRefreshArgs:
    """
    Represents arguments for refreshing buy/sell data
    """

    #region init

    def __init__(self,\
            bsmax:float, bsmin:float,\
            fun_buy:_func_buy, fun_sell:_func_sell):
        """
        Initializer for BuSeDataRefreshArgs

        :param bsmax:
            Maximum "fractional" difference before buying crypto
        :param bsmin:
            Minimum "fractional" difference before selling crypto
        :param fun_buy:
            Function for buying
        :param fun_sell:
            Function for selling
        """
        super().__init__()
        self.__bsmax = bsmax
        self.__bsmin = bsmin
        self.__fun_buy = fun_buy
        self.__fun_sell = fun_sell

    #endregion

    #region properties
    
    @property
    def bsmax(self):
        """
        Maximum "fractional" difference before buying crypto
        """
        return self.__bsmax
    
    @property
    def bsmin(self):
        """
        Minimum "fractional" difference before selling crypto
        """
        return self.__bsmin
    
    @property
    def fun_buy(self):
        """
        Function for buying
        """
        return self.__fun_buy
    
    @property
    def fun_sell(self):
        """
        Function for selling
        """
        return self.__fun_sell

    #endregion
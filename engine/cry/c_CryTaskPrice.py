all = ['CryTaskPrice']

import ccxt as _ccxt

from ..helper.c_CLIError import\
    CLIError as _CLIError
from .c_CryTask import\
    CryTask as _CryTask

class CryTaskPrice(_CryTask):
    """
    Represents a task to get the price for a pair\n
    Example: For the pair BTC/USD, this will fetch the BTC price.
    """

    #region init

    def __init__(self, symbol:str):
        """
        Initializer for CryTaskPrice

        :param symbol:
            Symbol (ex: 'BTC/USD')
        """
        super().__init__()
        self.__symbol = symbol
        self.__price = 0.0

    #endregion

    #region properties

    @property
    def symbol(self):
        """
        Symbol (ex: 'BTC/USD')
        """
        return self.__symbol

    @property
    def price(self):
        """
        Price
        """
        return self.__price

    #endregion

    #region CryTask
    
    def _main(self, exchange:_ccxt.coinbase):
        try:
            ticker = exchange.fetch_ticker(self.__symbol)
            self.__price = float(ticker['last']) # type: ignore
            return
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    #endregion
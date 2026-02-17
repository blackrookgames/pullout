all = ['CryTaskBalance']

import ccxt as _ccxt

from ..helper.c_CLIError import\
    CLIError as _CLIError
from .c_CryTask import\
    CryTask as _CryTask

class CryTaskBalance(_CryTask):
    """
    Represents a task to get the balance total for a currency
    """

    #region init

    def __init__(self, currency:str):
        """
        Initializer for CryTaskBalance

        :param currency:
            currency key
        """
        super().__init__()
        self.__currency = currency
        self.__total = 0.0

    #endregion

    #region properties

    @property
    def currency(self):
        """
        Currency key
        """
        return self.__currency

    @property
    def total(self):
        """
        Balance total
        """
        return self.__total

    #endregion

    #region CryTask
    
    def _main(self, exchange:_ccxt.coinbase):
        try:
            balance = exchange.fetch_balance()
            total = balance.get(self.__currency, {}).get('total', 0)
            self.__total = float(total) # type: ignore
            return
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    #endregion
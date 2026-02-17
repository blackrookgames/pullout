all = ['CryTaskLoad']

import ccxt as _ccxt

from ..helper.c_CLIError import\
    CLIError as _CLIError
from .c_CryTask import\
    CryTask as _CryTask

class CryTaskLoad(_CryTask):
    """
    Represents a task to load the markets
    """

    #region init

    def __init__(self, reload:bool = False):
        """
        Initializer for CryTaskLoad

        :param reload:
            Whether or not to force a reload of the markets
        """
        super().__init__()
        self.__reload = reload
        self.__markets:dict = {}

    #endregion

    #region properties

    @property
    def markets(self):
        """
        Dictionary of the loaded markets
        """
        return self.__markets

    #endregion

    #region CryTask
    
    def _main(self, exchange:_ccxt.coinbase):
        try:
            self.__markets = exchange.load_markets(reload = self.__reload)
            return
        except Exception as _e:
            e = _CLIError(_e)
        raise e

    #endregion
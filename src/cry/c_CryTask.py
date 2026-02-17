all = ['CryTask']

import ccxt as _ccxt

from .c_CryTaskStatus import\
    CryTaskStatus as _CryTaskStatus

class CryTask:
    """
    Represents a crypto-related task
    """

    #region init

    def __init__(self):
        """
        Initializer for CryTask
        """
        self.__status = _CryTaskStatus.INIT

    #endregion

    #region properties

    @property
    def status(self):
        """
        Task status
        """
        return self.__status

    #endregion

    #region helper methods

    def _run(self, exchange:_ccxt.coinbase):
        """
        Also accessed by ./__init__.py

        :raise CLIError:
            An error occurred
        """
        if self.__status != _CryTaskStatus.INIT: return
        self.__status = _CryTaskStatus.RUN
        self._main(exchange)
        self.__status = _CryTaskStatus.FINISH

    def _main(self, exchange:_ccxt.coinbase):
        """
        :raise CLIError:
            An error occurred
        """
        raise NotImplementedError("_main has not yet been implemented.")

    #endregion
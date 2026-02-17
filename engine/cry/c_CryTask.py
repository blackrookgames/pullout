all = ['CryTask']

import ccxt as _ccxt

from ..helper.c_CLIError import\
    CLIError as _CLIError
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
        self.__error:None|_CLIError = None

    #endregion

    #region properties

    @property
    def status(self):
        """
        Task status
        """
        return self.__status

    @property
    def error(self):
        """
        Error that occurred during execution. 
        If task completed successfully, this value is None.
        """
        return self.__error

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
        try:
            self._main(exchange)
            self.__status = _CryTaskStatus.SUCCESS
        except _CLIError as _e:
            self.__status = _CryTaskStatus.ERROR
            self.__error = _e

    def _main(self, exchange:_ccxt.coinbase):
        """
        :raise CLIError:
            An error occurred
        """
        raise NotImplementedError("_main has not yet been implemented.")

    #endregion

    #region methods

    def stillrunning(self):
        """
        Checks if the task is still executing (or waiting to be executed)
        
        :return:
            False if status == SUCCESS or status == ERROR; otherwise True
        """
        if self.__status == _CryTaskStatus.SUCCESS: return False
        if self.__status == _CryTaskStatus.ERROR: return False
        return True

    #endregion
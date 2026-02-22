all = ['CLIError']

import ccxt as _ccxt

from .c_CLIErrorType import\
    CLIErrorType as _CLIErrorType

class CLIError(Exception):
    """
    Raised when a CLI-related error occurs
    """
    
    #region init

    def __init__(self,\
            arg:object,\
            etype:None|_CLIErrorType = None):
        """
        Initializer for CLIError
        
        :param arg:
            Inner argument
        :param etype:
            Error type
        """
        super().__init__(arg)
        # etype
        if etype is None:
            if isinstance(arg, _ccxt.DDoSProtection):
                etype = _CLIErrorType.DDOS
            elif isinstance(arg, _ccxt.NetworkError):
                etype = _CLIErrorType.NETWORK
            elif isinstance(arg, _ccxt.InsufficientFunds):
                etype = _CLIErrorType.INSUFFICIENT
            else:
                etype = _CLIErrorType.MISC
        self.__etype = etype

    #endregion

    #region properties

    @property
    def etype(self):
        """
        Error type
        """
        return self.__etype

    #endregion
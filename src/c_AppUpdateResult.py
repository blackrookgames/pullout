all = ['AppUpdateResult']

from .inner.c_CLIError import\
    CLIError as _CLIError

class AppUpdateResult:
    """
    Represents the result of an update
    """

    #region init

    def __init__(self, error:None|_CLIError = None):
        """
        Initializer for AppUpdateResult

        :param error:
            Error that occurred during update
        """
        self.__error = error
        
    #endregion

    #region properties
    
    @property
    def error(self):
        """
        Error that occurred during update
        """
        return self.__error

    #endregion
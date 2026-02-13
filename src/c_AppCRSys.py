all = ['AppCRSys']

from .c_AppCR import\
    AppCR as _AppCR
from .c_AppCRType import\
    AppCRType as _AppCRType
from .c_AppCRWait import\
    AppCRWait as _AppCRWait

class AppCRSys:
    """
    Represents a coroutine system
    """

    #region init

    def __init__(self):
        """
        Initializer for AppCRSys

        :param coroutine:
            Actual coroutine generator
        """
        self.__coroutines:list[_AppCR] = []
        
    #endregion

    #region methods

    def start(self, coroutine:_AppCRType):
        """
        Starts a coroutine

        :param coroutine:
            Coroutine generator
        """
        self.__coroutines.append(_AppCR(coroutine))

    def update(self):
        """
        Update routine
        """
        _i = 0
        while _i < len(self.__coroutines):
            _cr = self.__coroutines[_i]
            _cr.update()
            if _cr.finish: self.__coroutines.pop(_i)
            else: _i += 1
    
    def running(self):
        """
        Checks if there are any coroutines that are currently running
        
        :return:
            Whether or not there are any running coroutines
        """
        return len(self.__coroutines) > 0


    #endregion
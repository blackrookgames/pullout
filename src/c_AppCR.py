all = ['AppCR']

from .c_AppCRType import\
    AppCRType as _AppCRType
from .c_AppCRWait import\
    AppCRWait as _AppCRWait

class AppCR:
    """
    Represents a coroutine
    """

    #region init

    def __init__(self, coroutine:_AppCRType):
        """
        Initializer for AppCR

        :param coroutine:
            Actual coroutine generator
        """
        self.__coroutine = coroutine
        self.__finish = False
        self.__wait = None
        self.update(0.0) # This is the first update; delta is 0.0
        
    #endregion

    #region properties
    
    @property
    def finish(self):
        """
        Whether or not coroutine has finished executing
        """
        return self.__finish

    #endregion

    #region methods
    
    def update(self, delta:float):
        """
        Update routine

        :param delta:
            Seconds since last update
        """
        if self.__finish: return
        # Update wait
        if self.__wait is not None and self.__wait.pause:
            self.__wait.update(delta)
        # Next wait
        if self.__wait is None or (not self.__wait.pause):
            self.__wait = next(self.__coroutine, None)
            if self.__wait is None: self.__finish = True

    #endregion
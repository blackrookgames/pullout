all = []

from .c_CRGen import\
    CRGen as _CRGen
from .c_CRWait import\
    CRWait as _CRWait

class _CRCoroutine:
    """
    Represents a coroutine
    """

    #region init

    def __init__(self, coroutine:_CRGen):
        """
        Initializer for _CRCoroutine

        :param coroutine:
            Actual coroutine generator
        """
        self.__coroutine = coroutine
        self.__finish = False
        self.__wait = None
        self._update(0.0) # This is the first update; delta is 0.0
        
    #endregion

    #region properties
    
    @property
    def finish(self):
        """
        Whether or not coroutine has finished executing
        """
        return self.__finish

    #endregion

    #region helper methods
    
    def _update(self, delta:float):
        """
        Assume
        - delta >= 0.0
        \n
        Also accessed by __init__
        """
        if self.__finish: return
        # Update wait
        if self.__wait is not None and self.__wait.waiting:
            self.__wait._update(delta)
        # Next wait
        if self.__wait is None or (not self.__wait.waiting):
            self.__wait = next(self.__coroutine, None)
            if self.__wait is None: self.__finish = True

    #endregion
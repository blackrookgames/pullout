all = ['CRWaitTime']

from .c_CRWait import\
    CRWait as _CRWait

class CRWaitTime(_CRWait):
    """
    Represents a wait for a certain length of time
    """

    #region init

    def __init__(self, delay:float):
        """
        Initializer for CRWaitTime

        :param delay:
            Length of time to wait
        """
        super().__init__()
        self.__delay = delay
        self.__time = 0.0

    #endregion

    #region helper methods

    def _update(self, delta:float):
        self.__time += delta
        if self.__time >= self.__delay:
            self._stopwait()

    #endregion
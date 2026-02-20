all = ['CRWaitWhile']

from typing import\
    Callable as _Callable

from .c_CRWait import\
    CRWait as _CRWait

class CRWaitWhile(_CRWait):
    """
    Represents a wait while a condition is true
    """

    #region init

    def __init__(self, condition:_Callable[[], bool]):
        """
        Initializer for CRWaitWhile

        :param condition:
            Condition to test
        """
        super().__init__()
        self.__condition = condition

    #endregion

    #region helper methods

    def _update(self, delta:float):
        if not self.__condition():
            self._stopwait()

    #endregion
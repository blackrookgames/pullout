all = ['CryTaskWait']

from ..coroutine.c_CRWait import\
    CRWait as _CRWait
from .c_CryTask import\
    CryTask as _CryTask
from .c_CryTaskStatus import\
    CryTaskStatus as _CryTaskStatus

class CryTaskWait(_CRWait):
    """
    Represents a wait while a task is running
    """

    #region init

    def __init__(self, task:_CryTask):
        """
        Initializer for CryTaskWait

        :param task:
            Task to wait for
        """
        super().__init__()
        self.__task = task

    #endregion
    
    #region helper methods

    def _update(self, delta:float):
        if not self.__task.stillrunning():
            self._stopwait()

    #endregion
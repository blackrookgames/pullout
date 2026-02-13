all = ['AppCRWaitUpdate']

from .c_AppCRWait import\
    AppCRWait as _AppCRWait

class AppCRWaitTime(_AppCRWait):
    """
    Represents a wait for a certain length of time
    """

    #region init

    def __init__(self, delay:float):
        """
        Initializer for AppCRWaitTime

        :param delay:
            Length of time to wait
        """
        super().__init__()
        self.__delay = delay
        self.__time = 0.0

    #endregion

    #region methods

    def update(self, delta:float):
        self.__time += delta
        if self.__time >= self.__delay:
            self._unpause()

    #endregion
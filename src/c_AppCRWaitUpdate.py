all = ['AppCRWaitUpdate']

from .c_AppCRWait import\
    AppCRWait as _AppCRWait

class AppCRWaitUpdate(_AppCRWait):
    """
    Represents a wait till the next update
    """

    #regionmethods

    def update(self, delta:float):
        self._unpause()

    #endregion
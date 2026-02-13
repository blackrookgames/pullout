all = ['AppCRWaitUpdate']

from .c_AppCRWait import\
    AppCRWait as _AppCRWait

class AppCRWaitUpdate(_AppCRWait):
    """
    Represents a wait till the next update
    """

    #region methods

    def update(self):
        self._unpause()

    #endregion
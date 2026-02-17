all = ['AppObject']

from .c_AppUpdate import\
    AppUpdate as _AppUpdate

class AppObject:
    """
    Represents an application object
    """

    #region init

    def __init__(self):
        """
        Initializer for AppObject
        """
        self.__active = False

    #endregion

    #region properties

    @property
    def active(self):
        """
        Whether or not the object is active.\n
        To activate the object call app.object_add().\n
        To deactivate the object call app.object_remove().\n
        """
        return self.__active

    #endregion

    #region helper methods

    def _set_active(self, value:bool):
        """
        Also accessed by ./__init__.py
        """
        if self.__active == value: return
        self.__active = value
        if self.__active: self._activated()
        else: self._deactivated()

    def _update(self, params:_AppUpdate):
        """
        Update routine\n
        Also accessed by ./__init__.py
        """
        pass

    def _activated(self):
        """
        Called when the object is activated
        """
        pass

    def _deactivated(self):
        """
        Called when the object is deactivated
        """
        pass

    #endregion
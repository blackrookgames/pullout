all = ['AppObject']

from typing import\
    TYPE_CHECKING as _TYPE_CHECKING

from .c_AppUpdate import\
    AppUpdate as _AppUpdate

if _TYPE_CHECKING:
    from .__init__ import\
        _m_focus_update

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
        self.__focusable = False
        self.__hasfocus = False

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

    @property
    def focusable(self):
        """
        Whether or not the object can be focused on
        """
        return self.__focusable
    @focusable.setter
    def focusable(self, value:bool):
        if self.__focusable == value: return
        self.__focusable = value
        self.__focus_update()

    @property
    def hasfocus(self):
        """
        Whether or not the object has focus
        """
        return self.__hasfocus

    #endregion

    #region helper methods
    
    def __focus_update(self):
        try:
            _m_focus_update(None) # type: ignore
            return 
        except NameError as _e:
            if not ('_m_focus_update' in locals()):
                return
            e = _e
        raise e

    def _set_active(self, value:bool):
        """
        Also accessed by ./__init__.py
        """
        if self.__active == value: return
        self.__active = value
        if self.__active: self._activated()
        else: self._deactivated()

    def _set_focus(self, value:bool):
        """
        Also accessed by ./__init__.py
        """
        # Do NOT call methods; that's handled separately
        self.__hasfocus = value

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

    def _focus_gained(self):
        """
        Called when the object has gained focus\n
        Also accessed by ./__init__.py
        """
        pass

    def _focus_lost(self):
        """
        Called when the object has lost focus\n
        Also accessed by ./__init__.py
        """
        pass

    #endregion
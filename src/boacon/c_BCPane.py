all = ['BCPane']

import numpy as _np

from typing import\
    Callable as _Callable

from .c_BCChar import\
    BCChar as _BCChar
from .c_BCCoord import\
    BCCoord as _BCCoord

class BCPane:
    """
    Represents a pane
    """

    #region init

    def __init__(self):
        """
        Initializer for BCPane
        """
        self.__x = _BCCoord()
        self.__y = _BCCoord()
        self.__dirty = False

    #endregion

    #region properties

    @property
    def x(self):
        """
        X-coordinates
        """
        return self.__x

    @property
    def y(self):
        """
        Y-coordinates
        """
        return self.__y

    #endregion

    #region helper methods
    
    def _m_resolve(self, resized:bool, console_w:int, console_h:int):
        """
        Assume
        - console_w >= 0
        - console_h >= 0
        \n
        Also accessed by functions
        """
        resolve_x = self.__x._m_resolve(resized, console_w)
        resolve_y = self.__y._m_resolve(resized, console_h)
        if not (resolve_x or resolve_y): return False
        self._resolved()
        self.__dirty = True
        return True

    def _m_refresh(self, force:bool, setchr:_Callable[[int, int, _BCChar], None]):
        """
        Also accessed by functions
        """
        dirty = self.__dirty or force
        self.__dirty = False
        if dirty: self._draw(setchr)
    
    def _resolved(self):
        """
        Called after panes dimensions have been resolved
        """
        pass
    
    def _draw(self, setchr:_Callable[[int, int, _BCChar], None]):
        """
        Draws the pane

        :param setchr:
            Function for putting characters on the screen; parameters are x, y, and char
        """
        pass

    #endregion

    #region methods

    def set_dirty(self):
        """
        Marks the pane as dirty
        """
        self.__dirty = True

    #endregion
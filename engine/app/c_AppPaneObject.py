all = ['AppPaneObject']

import numpy as _np

from typing import\
    Callable as _Callable

from engine.boacon import\
    BCChar as _BCChar,\
    BCPane as _BCPane,\
    panes as _panes
from .c_AppObject import\
    AppObject as _AppObject
from .c_AppPaneObjectCharBuffer import\
    AppPaneObjectCharBuffer as _AppPaneObjectCharBuffer

class AppPaneObject(_AppObject, _BCPane):
    """
    Represents an application object and a boacon pane
    """

    #region init

    def __init__(self):
        """
        Initializer for AppPaneObject
        """
        _AppObject.__init__(self)
        _BCPane.__init__(self)
        self.__chars = _AppPaneObjectCharBuffer()

    #endregion

    #region helper properties

    @property
    def _chars(self): return self.__chars

    #endregion

    #region helper methods
    
    def _refreshbuffer(self):
        """
        Called when the character buffer needs to be refreshed\n
        Assume:
        - _chrs_w > 0
        - _chrs_h > 0
        - len(_chrs) == (_chrs_w * _chrs_h)
        """
        pass

    def _update_chrs(self):
        # Make sure pane has a valid size
        if len(self.__chars) == 0: return
        # Refresh
        self._refreshbuffer()
        # Mark dirty
        self.set_dirty()

    #endregion

    #region AppObject

    def _activated(self):
        super()._activated()
        _panes().append(self)

    def _deactivated(self):
        super()._deactivated()
        _panes().remove(self)

    #endregion

    #region BCPane
    
    def _resolved(self):
        super()._resolved()
        if self.__chars.width == self.x.pntlen and\
            self.__chars.height == self.y.pntlen: return
        self.__chars._format(\
            max(0, self.x.pntlen), max(0, self.y.pntlen))
        self._update_chrs()

    def _draw(self,\
            setchr:_Callable[[int, int, _BCChar], None]):
        super()._draw(setchr)
        # Make sure pane has a valid size
        if len(self.__chars) == 0: return
        # Copy to screen
        iy = self.y.clipoff
        oy = self.y.clip0
        while oy < self.y.clip1:
            ix = self.x.clipoff
            ox = self.x.clip0
            while ox < self.x.clip1:
                setchr(ox, oy, self.__chars[iy * self.__chars.width + ix])
                ix += 1
                ox += 1
            iy += 1
            oy += 1

    #endregion
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
        self.__chrs_w = 0
        self.__chrs_h = 0
        self.__chrs = _np.full(0, _BCChar(0x20), dtype = object)

    #endregion

    #region helper properties

    @property
    def _chrs_w(self): return self.__chrs_w

    @property
    def _chrs_h(self): return self.__chrs_h

    @property
    def _chrs(self): return self.__chrs

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

    def __update_chrs(self):
        # Make sure pane has a valid size
        if self.__chrs_w == 0 or self.__chrs_h == 0:
            return
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
        if self.__chrs_w == self.x.pntlen and self.__chrs_h == self.y.pntlen:
            return
        self.__chrs_w = max(0, self.x.pntlen)
        self.__chrs_h = max(0, self.y.pntlen)
        self.__chrs = _np.full(\
            self.__chrs_w * self.__chrs_h, _BCChar(0x20), dtype = object)
        self.__update_chrs()

    def _draw(self,\
            setchr:_Callable[[int, int, _BCChar], None]):
        super()._draw(setchr)
        # Make sure pane has a valid size
        if self.__chrs_w == 0 or self.__chrs_h == 0:
            return
        # Copy to screen
        iy = self.y.clipoff
        oy = self.y.clip0
        while oy < self.y.clip1:
            ix = self.x.clipoff
            ox = self.x.clip0
            while ox < self.x.clip1:
                setchr(ox, oy, self.__chrs[iy * self.__chrs_w + ix])
                ix += 1
                ox += 1
            iy += 1
            oy += 1

    #endregion
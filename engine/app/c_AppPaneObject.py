all = ['AppPaneObject']

import numpy as _np

from curses import\
    window as _window
from typing import\
    Callable as _Callable

from engine.boacon import\
    BCChar as _BCChar,\
    BCPane as _BCPane,\
    BCPostDrawArgs as _BCPostDrawArgs,\
    panes as _panes,\
    postdraw as _postdraw
from .c_AppObject import\
    AppObject as _AppObject
from .c_AppPaneObjectCharBuffer import\
    AppPaneObjectCharBuffer as _AppPaneObjectCharBuffer

_CHAR_H = chr(0x2501)
_CHAR_V = chr(0x2503)
_CHAR_TL = chr(0x250F)
_CHAR_TR = chr(0x2513)
_CHAR_BL = chr(0x2517)
_CHAR_BR = chr(0x251B)

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
        self.__border = True

    #endregion

    #region helper properties

    @property
    def _chars(self): return self.__chars

    #endregion

    #region properties
    
    @property
    def border(self):
        """
        Whether or not the pane has a border
        """
        return self.__border
    @border.setter
    def border(self, value:bool):
        if self.__border == value: return
        self.__border = value
    
    #endregion

    #region receivers

    def __r_postdraw(self, args:_BCPostDrawArgs):
        def _draw_chr(_x:int, _y:int, _chr:str):
            nonlocal args
            try: args.win.addch(_y, _x, _chr)
            except: pass
        def _draw_chrs(_x:int, _y:int, _chr:str, _len:int):
            nonlocal args
            try: args.win.addstr(_y, _x, _chr * _len)
            except: pass
        # Draw border (if specified)
        if self.__border and self.x.cliplen >= 0 and self.y.cliplen >= 0:
            _win_h, _win_w = args.win.getmaxyx()
            _draw_left = self.x.clip0 > 0
            _draw_right = self.x.clip1 < _win_w
            _draw_top = self.y.clip0 > 0
            _draw_bottom = self.y.clip1 < _win_h
            # Draw top
            if _draw_top:
                if _draw_left:
                    _draw_chr(self.x.clip0 - 1, self.y.clip0 - 1, _CHAR_TL)
                if _draw_right:
                    _draw_chr(self.x.clip1, self.y.clip0 - 1, _CHAR_TR)
                _draw_chrs(self.x.clip0, self.y.clip0 - 1, _CHAR_H, self.x.cliplen)
            # Draw bottom
            if _draw_bottom:
                if _draw_left:
                    _draw_chr(self.x.clip0 - 1, self.y.clip1, _CHAR_BL)
                if _draw_right:
                    _draw_chr(self.x.clip1, self.y.clip1, _CHAR_BR)
                _draw_chrs(self.x.clip0, self.y.clip1, _CHAR_H, self.x.cliplen)
            # Draw left
            if _draw_left:
                for _i in range(self.y.cliplen):
                    _draw_chr(self.x.clip0 - 1, self.y.clip0 + _i, _CHAR_V)
            # Draw right
            if _draw_right:
                for _i in range(self.y.cliplen):
                    _draw_chr(self.x.clip1, self.y.clip0 + _i, _CHAR_V)
            
        # Call additional
        self._postdraw()
    
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
    
    def _postdraw(self):
        """
        Called during the post draw period of boacon
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
        # Add to panes
        _panes().append(self)
        _postdraw().connect(self.__r_postdraw)
        

    def _deactivated(self):
        super()._deactivated()
        # Remove from panes
        _postdraw().disconnect(self.__r_postdraw)
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
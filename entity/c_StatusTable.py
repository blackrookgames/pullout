all = ['StatusTable']

import curses as _curses
import math as _math

from collections.abc import\
    Iterable as _Iterable
from typing import\
    Callable as _Callable,\
    cast as _cast

import cry as _cry
import engine.app as _app
import engine.boacon as _boacon
import engine.coroutine as _coroutine
import engine.helper as _helper

from .c_CryptoSignal import\
    CryptoSignal as _CryptoSignal
from .c_CryptoSignalEmitter import\
    CryptoSignalEmitter as _CryptoSignalEmitter
from .c_CryptoStats import\
    CryptoStats as _CryptoStats

_WIDTH_ROWNUM = 6
_WIDTH_SYMBOL = 10
_WIDTH_PRICE = 20
_HEADER = _boacon.BCStr((\
    _boacon.BCStr("  #".ljust(_WIDTH_ROWNUM)),\
    _boacon.BCStr("Symbol".ljust(_WIDTH_SYMBOL)),\
    _boacon.BCStr("Price".ljust(_WIDTH_PRICE))))

_LV_TOP = 2
_LV_BOTTOM = 2
_LV_TIMER = 5.0

class StatusTable(_app.AppPaneObject):
    """
    Represents a table displaying the current status of currencies
    """

    #region init

    def __init__(self,\
            crypto:_CryptoStats,\
            dtformat:_helper.DTFormat):
        """
        Initializer for StatusTable

        :params crypto:
            CryptoStats handler
        :params dtformat:
            Date/time format
        """
        super().__init__()
        # List view
        self.__lv_show = False
        self.__lv_index = -1
        self.__lv_offset = 0
        self.__lv_height = 0
        self.__lv_timer = 0.0
        # Selected index
        self.__selindex = -1
        self.__selindex_changed_e = _CryptoSignalEmitter()
        self.__selindex_changed = _CryptoSignal(self.__selindex_changed_e)
        # Recieve signals
        self.__crypto = crypto
        self.__crypto.newstats.connect(self.__r_newstats)
        # Date/time format
        self.__dtformat = dtformat

    #endregion

    #region properties/signals

    @property
    def selindex(self):
        """
        Index of the currently selected item
        """
        return self.__selindex

    @property
    def selindex_changed(self):
        """
        Emitted when the selected index is changed
        """
        return self.__selindex_changed

    #endregion

    #region receivers

    def __r_newstats(self):
        self.__lv_show = True
        self.__lv_update(None)

    #endregion

    #region helper methods
    
    def __lv_update(self, index:None|int):
        # Update index
        if index is not None:
            self.__lv_index = index
        self.__lv_index = max(-1,\
            min(len(self.__crypto.stats) - 1, self.__lv_index))
        # Update view
        view_height = self._chars.height - _LV_TOP - _LV_BOTTOM
        if view_height > 0:
            if view_height < len(self.__crypto.stats):
                # Scroll to selected index
                if self.__lv_offset > self.__lv_index:
                    self.__lv_offset = self.__lv_index
                if (self.__lv_offset + view_height) <= self.__lv_index:
                    self.__lv_offset = self.__lv_index + 1 - view_height
                if self.__lv_offset < 0:
                    self.__lv_offset = 0
                # Set height
                self.__lv_height = view_height
            else:
                self.__lv_offset = 0
                self.__lv_height = len(self.__crypto.stats)
        else:
            self.__lv_offset = 0
            self.__lv_height = 0
        # Update selected index
        self.__selindex_set(self.__lv_index if (self.__lv_timer > 0.0) else -1)
        # Update buffer
        self._update_chrs()

    def __selindex_set(self, value:int):
        if self.__selindex == value: return
        self.__selindex = value
        self.__selindex_changed_e.emit()

    #endregion

    #region AppObjectPane
    
    def _refreshbuffer(self):
        super()._refreshbuffer()
        _SPACE = _boacon.BCChar(0x20)
        _oindex = 0
        # Format date/time of last updated
        dt = self.__dtformat.create(self.__crypto.stats_updated)
        dt = f"Last updated {dt} "
        if len(dt) > self._chars.width:
            dt = dt[(-self._chars.width):]
        # Draw header
        _rest = self._chars.width
        for _i in range(min(len(_HEADER), _rest)):
            self._chars[_oindex] = _HEADER[_i]
            _rest -= 1
            _oindex += 1
        while _rest > 0:
            self._chars[_oindex] = _SPACE
            _rest -= 1
            _oindex += 1
        # Draw space
        _rest = (_LV_TOP * self._chars.width) - _oindex
        while _rest > 0:
            _rest -= 1
            self._chars[_oindex] = _SPACE
            _oindex += 1
        # Draw rows
        if self.__lv_show:
            for _i in range(self.__lv_height):
                _index = self.__lv_offset + _i
                _rest = self._chars.width
                _stat = self.__crypto.stats[_index]
                # Attributes
                _attr = _boacon.attr_create(\
                    emp = self.__lv_timer > 0.0 and\
                        _index == self.__lv_index)
                # Row number
                _str = str(_index + 1).rjust(3).ljust(_WIDTH_ROWNUM)
                for _j in range(min(_WIDTH_ROWNUM, _rest)):
                    self._chars[_oindex] = _boacon.BCChar(\
                        ord(_str[-_WIDTH_ROWNUM + _j]),\
                        attr = _attr)
                    _rest -= 1
                    _oindex += 1
                # Symbol
                _str = _stat.currency.ljust(_WIDTH_SYMBOL)
                for _j in range(min(_WIDTH_SYMBOL, _rest)):
                    self._chars[_oindex] = _boacon.BCChar(\
                        ord(_str[_j]), attr = _attr)
                    _rest -= 1
                    _oindex += 1
                # Price
                _str = str(_stat.price).ljust(_WIDTH_PRICE)
                for _j in range(min(_WIDTH_PRICE, _rest)):
                    self._chars[_oindex] = _boacon.BCChar(\
                        ord(_str[_j]), attr = _attr)
                    _rest -= 1
                    _oindex += 1
                # Fill rest of row
                while _rest > 0:
                    self._chars[_oindex] = _boacon.BCChar(\
                        0x20, attr = _attr)
                    _rest -= 1
                    _oindex += 1
        # Draw space
        _rest = len(self._chars) - len(dt) - _oindex
        while _rest > 0:
            _rest -= 1
            self._chars[_oindex] = _SPACE
            _oindex += 1
        # Draw date/time
        for _chr in dt:
            self._chars[_oindex] = _boacon.BCChar(ord(_chr))
            _oindex += 1

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        def _reset_timer():
            _timerwas0 = self.__lv_timer == 0.0
            self.__lv_timer = _LV_TIMER
            return _timerwas0
        super()._update(params)
        # Get keyboard input
        update_lv_timer = True
        match params.key:
            case _curses.KEY_UP:
                self.__lv_update(\
                    None if _reset_timer()\
                    else max(0, self.__lv_index - 1))
                update_lv_timer = False
            case _curses.KEY_DOWN:
                self.__lv_update(\
                    None if _reset_timer()\
                    else (self.__lv_index + 1))
                update_lv_timer = False
        # Update timer
        if update_lv_timer:
            if self.__lv_timer > 0.0:
                self.__lv_timer -= params.delta
                if self.__lv_timer <= 0.0:
                    self.__lv_timer = 0.0
                    self.__selindex_set(-1)
                    self._update_chrs()

    def _activated(self):
        super()._activated()

    def _deactivated(self):
        super()._deactivated()

    #endregion

    #region BCPane
    
    def _resolved(self):
        super()._resolved()
        self.__lv_update(None)

    def _draw(self,\
            setchr:_Callable[[int, int, _boacon.BCChar], None]):
        super()._draw(setchr)
        
    #endregion
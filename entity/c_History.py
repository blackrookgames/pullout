all = ['History']

import curses as _curses

from typing import\
    Callable as _Callable,\
    cast as _cast

import cry as _cry
import engine.app as _app
import engine.boacon as _boacon
import engine.helper as _helper

from .c_HistoryData import\
    HistoryData as _HistoryData
from .c_CryptoKeeper import\
    CryptoKeeper as _CryptoKeeper
from .c_StatusTable import\
    StatusTable as _StatusTable

_SPACE = _boacon.BCChar(0x20)
_ARROW_UP = _boacon.BCChar(0x2191)
_ARROW_DOWN = _boacon.BCChar(0x2193)

class History(_app.AppPaneObject):
    """
    Represents a display of price history
    """

    #region init

    def __init__(self,\
            keeper:_CryptoKeeper,\
            table:_StatusTable,\
            dtformat:_helper.DTFormat):
        """
        Initializer for History

        :params keeper:
            Crypto keeper
        :params table:
            Crypto status table
        :params dtformat:
            Date/time format
        """
        super().__init__()
        self.focusable = True
        # Crypto keeper
        self.__keeper = keeper
        self.__keeper.refreshed.connect(self.__r_keeper_refreshed)
        # Status table
        self.__table = table
        self.__table.selection_changed.connect(self.__r_table_selection_changed)
        # Date/time format
        self.__dtformat = dtformat
        # Crypto entries
        self.__entries:dict[str, _HistoryData] = {}
        # Active crypto (one being displayed)
        self.__active:None|str = None
        # View
        self.__view_offset = 0 # Offset progresses upward

    #endregion

    #region receivers

    def __r_keeper_refreshed(self):
        # Add entries (if needed)
        if len(self.__entries) == 0:
            for _crypto in self.__keeper.prices:
                self.__entries[_crypto.name] = _HistoryData(self.__keeper, _crypto.name, 20)
        # Update entries
        for _crypto in self.__keeper.prices:
            self.__entries[_crypto.name]._refresh()
        # If no crypto is active, find one to be active
        if self.__active is None:
            if len(self.__keeper.prices) > 0:
                self.__active = self.__keeper.prices[0].name
        # Update character buffer
        self._update_chrs()

    def __r_table_selection_changed(self):
        # Only change active is a crypto is being selected
        if self.__table.selcrypto is None: return
        # Change active crypto
        self.__active = self.__table.selcrypto
        # Reset view
        self.__view_offset = 0
        # Update character buffer
        self._update_chrs()

    #endregion

    #region AppObjectPane
    
    def _refreshbuffer(self):
        super()._refreshbuffer()
        def _draw_column(_start, _end, _colwidth, _str):
            nonlocal self
            # Draw string
            _rest = min(_end - _start, _colwidth)
            for _i in range(min(_rest, len(_str))):
                self._chars[_start] = _boacon.BCChar(ord(_str[_i]))
                _start += 1
                _rest -= 1
            # Fill rest of column
            while  _rest > 0:
                self._chars[_start] = _SPACE
                _start += 1
                _rest -= 1
            # Success!!!
            return _start
        if len(self._chars) > 0 and self.__active is not None:
            active = self.__entries[self.__active]
            if len(active.history) > 0:
                oindex = len(self._chars)
                # Fix view
                if (self.__view_offset + self._chars.height) > len(active.history):
                    self.__view_offset = len(active.history) - self._chars.height
                if self.__view_offset < 0:
                    self.__view_offset = 0
                # Draw history
                _view_offset_end = self.__view_offset + self._chars.height
                _view_at_start = self.__view_offset == 0
                _view_at_end = _view_offset_end >= len(active.history)
                for _i in range(self.__view_offset, len(active.history) if _view_at_end else _view_offset_end):
                    _xend = oindex
                    _marg = _xend - 2
                    oindex -= self._chars.width
                    _j = oindex
                    # Get history entry
                    _hentry = active.history[_i]
                    # Draw date
                    _j = _draw_column(_j, _marg, 30, f" {self.__dtformat.create(_hentry.dt)}")
                    # Draw price
                    _j = _draw_column(_j, _marg, 20, str(_hentry.price))
                    # Fill row
                    while _j < _xend:
                        self._chars[_j] = _SPACE
                        _j += 1
                # Fill rest
                while oindex > 0:
                    oindex -= 1
                    self._chars[oindex] = _SPACE
                # Add view arrows
                if not _view_at_start: self._chars[len(self._chars) - 1] = _ARROW_DOWN
                if not _view_at_end: self._chars[self._chars.width - 1] = _ARROW_UP
            else: self._chars.clear()
        else: self._chars.clear()

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)
        # Check keys
        if self.hasfocus:
            match params.key:
                case _curses.KEY_UP:
                    self.__view_offset += 1
                    self._update_chrs()
                case _curses.KEY_DOWN:
                    self.__view_offset -= 1
                    self._update_chrs()

    def _activated(self):
        super()._activated()

    def _deactivated(self):
        super()._deactivated()

    #endregion
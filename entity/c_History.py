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

    #endregion

    #region receivers

    def __r_keeper_refreshed(self):
        # Add entries (if needed)
        if len(self.__entries) == 0:
            for _crypto in self.__keeper.prices:
                self.__entries[_crypto.name] = _HistoryData(self.__keeper, _crypto.name)
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
        # Update character buffer
        self._update_chrs()

    #endregion

    #region AppObjectPane
    
    def _refreshbuffer(self):
        super()._refreshbuffer()
        _SPACE = _boacon.BCChar(0x20)
        oindex = 0
        # Test: placeholder
        _rest = self._chars.width
        _text = "History placeholder"
        for _i in range(min(_rest, len(_text))):
            self._chars[oindex] =  _boacon.BCChar(ord(_text[_i]))
            oindex += 1
            _rest -= 1
        while _rest > 0:
            self._chars[oindex] = _SPACE
            _rest -= 1
            oindex += 1
        # Test: spacing
        for _i in range(self._chars.width):
            self._chars[oindex] = _SPACE
            oindex += 1
        # Show active crypto
        if self.__active is not None:
            _entry = self.__entries[self.__active]
            _rest = self._chars.width
            # Test: name
            for _i in range(min(len(_entry.crypto), _rest)):
                self._chars[oindex] = _boacon.BCChar(ord(_entry.crypto[_i]))
                oindex += 1
                _rest -= 1
            # Test: space
            for _i in range(min(3, _rest)):
                self._chars[oindex] = _SPACE
                oindex += 1
                _rest -= 1
            # Test: date and price
            if len(_entry.history) > 0:
                _last = _entry.history[len(_entry.history) - 1]
                # Test: date/time
                _dt = self.__dtformat.create(_last.dt)
                for _i in range(min(len(_dt), _rest)):
                    self._chars[oindex] = _boacon.BCChar(ord(_dt[_i]))
                    oindex += 1
                    _rest -= 1
                # Test: space
                for _i in range(min(3, _rest)):
                    self._chars[oindex] = _SPACE
                    oindex += 1
                    _rest -= 1
                # Test: date/time
                _price = str(_last.price)
                for _i in range(min(len(_price), _rest)):
                    self._chars[oindex] = _boacon.BCChar(ord(_price[_i]))
                    oindex += 1
                    _rest -= 1
        # Fill rest
        if oindex < len(self._chars):
            self._chars[oindex] = _SPACE
            oindex += 1

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)

    def _activated(self):
        super()._activated()

    def _deactivated(self):
        super()._deactivated()

    #endregion
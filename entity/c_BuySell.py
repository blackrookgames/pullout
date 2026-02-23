all = ['BuySell']

import curses as _curses

from typing import\
    Callable as _Callable,\
    cast as _cast

import cry as _cry
import engine.app as _app
import engine.boacon as _boacon
import engine.helper as _helper

from .c_BuySellEntry import\
    BuySellEntry as _BuySellEntry
from .c_CryptoKeeper import\
    CryptoKeeper as _CryptoKeeper
from .c_StatusTable import\
    StatusTable as _StatusTable

class BuySell(_app.AppPaneObject):
    """
    Represents a handler for buying/selling
    """

    #region init

    def __init__(self,\
            crypto:_cry.Cry,\
            opparams:_cry.CryOpParams,\
            keeper:_CryptoKeeper,\
            table:_StatusTable):
        """
        Initializer for BuySell

        :params crypto:
            Crypto operation handler
        :params opparams:
            Parameters for Crypto-related operations
        :params keeper:
            Crypto keeper
        :params table:
            Crypto status table
        """
        super().__init__()
        # Crypto operation handler
        self.__crypto = crypto
        self.__opparams = opparams
        # Crypto keeper
        self.__keeper = keeper
        self.__keeper.refreshed.connect(self.__r_keeper_refreshed)
        # Status table
        self.__table = table
        self.__table.selection_changed.connect(self.__r_table_selection_changed)
        # Crypto entries
        self.__entries:dict[str, _BuySellEntry] = {}
        # Active crypto (one being displayed)
        self.__active:None|str = None

    #endregion

    #region receivers

    def __r_keeper_refreshed(self):
        # Add entries (if needed)
        updateentries = True
        if len(self.__entries) == 0:
            # Add entries
            _noncryptocount = 0
            for _crypto in self.__keeper.prices:
                _entry = _BuySellEntry(_crypto.name)
                # Price
                _entry.price = _crypto.value
                # Balance
                _entry.balance = self.__keeper.balances[_crypto.name].value
                if _entry.balance > 0.0: _entry.investing = True
                else: _noncryptocount += 1
                # Add entry
                self.__entries[_crypto.name] = _entry
            # Compute non-crypto fractions
            if _noncryptocount > 0:
                _fraction = 1.0 / _noncryptocount
                for _entry in self.__entries.values():
                    if not _entry.investing: _entry.noncrypto = _fraction
            # Don't update entries
            updateentries = False
        # Update entries
        if updateentries:
            for _entry in self.__entries.values():
                # Skip if compromised
                if _entry.compromised:
                    continue
                if not (_entry.name in self.__keeper.prices):
                    _entry.compromised = True
                    continue
                # Previous
                _prev_price = _entry.price
                _prev_balance = _entry.balance
                # Update
                _entry.price = self.__keeper.prices[_entry.name].value
                _entry.balance = self.__keeper.balances[_entry.name].value
                _entry.priceinc = _entry.price - _prev_price
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

    #region helper methods

    def __print(self, text:str):
        if self.__opparams.printfunc is not None:
            self.__opparams.printfunc(text)
        else:
            _app.console().print(text)

    #endregion

    #region AppObjectPane
    
    def _refreshbuffer(self):
        super()._refreshbuffer()
        _SPACE = _boacon.BCChar(0x20)
        _COLUMN = 15
        oindex = 0
        def _printline(_text:str):
            nonlocal self, oindex
            _text = _helper.StrUtil.ljusttrun(_text, self._chars.width)
            for _i in range(min(len(_text), len(self._chars) - oindex)):
                self._chars[oindex] = _boacon.BCChar(ord(_text[_i]))
                oindex += 1
        # Display active crypto
        if self.__active is not None and self.__active in self.__entries:
            _entry = self.__entries[self.__active]
            # Name
            _printline(f"{" Name:".ljust(_COLUMN)}{self.__active}")
            # Price
            _pcntinc = "" if (_entry.priceinc is None)\
                else ('-' if (_entry.priceinc == 0) else ('\u2193' if (_entry.priceinc < 0) else '\u2191'))
            _printline(f"{" Price:".ljust(_COLUMN)}{_entry.price} {_pcntinc}")
            # Balance or fraction
            if _entry.balance > 0.0:
                _printline(f"{" Balance:".ljust(_COLUMN)}{_entry.balance}")
            else: 
                _printline(f"{" Non-Crypto:".ljust(_COLUMN)}{round(_entry.noncrypto * 100.0, 5)}%")
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
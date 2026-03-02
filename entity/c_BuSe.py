all = ['BuSe']

import cry as _cry
import engine.app as _app
import engine.boacon as _boacon
import engine.helper as _helper

from .c_BuSeData import\
    BuSeData as _BuSeData
from .c_CryptoKeeper import\
    CryptoKeeper as _CryptoKeeper
from .c_StatusTable import\
    StatusTable as _StatusTable

_SPACE = _boacon.BCChar(0x20)

class BuSe(_app.AppPaneObject):
    """
    Represents a handler for buying and selling
    """

    #region init

    def __init__(self,\
            crypto:_cry.Cry,\
            opparams:_cry.CryOpParams,\
            keeper:_CryptoKeeper,\
            table:_StatusTable,\
            trlen:int,\
            dtformat:_helper.DTFormat):
        """
        Initializer for BuSe

        :params crypto:
            Crypto operation handler
        :params opparams:
            Parameters for Crypto-related operations
        :params keeper:
            Crypto keeper
        :params table:
            Crypto status table
        :param trlen:
            Length of time (in microseconds) to look back before making a decision to buy or sell
        """
        super().__init__()
        self.focusable = True
        # Crypto operation handler
        self.__crypto = crypto
        self.__opparams = opparams
        # Crypto keeper
        self.__keeper = keeper
        self.__keeper.refreshed.connect(self.__r_keeper_refreshed)
        # Status table
        self.__table = table
        self.__table.selection_changed.connect(self.__r_table_selection_changed)
        # Train interval
        self.__trlen = max(1, trlen)
        # Date/time format
        self.__dtformat = dtformat
        # Crypto entries
        self.__entries:dict[str, _BuSeData] = {}
        # Active crypto (one being displayed)
        self.__active:None|str = None

    #endregion

    #region receivers

    def __r_keeper_refreshed(self):
        # Add entries (if needed)
        if len(self.__entries) == 0:
            for _crypto in self.__keeper.prices:
                self.__entries[_crypto.name] = _BuSeData(self.__keeper, _crypto.name, self.__trlen)
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
        if len(self._chars) > 0 and self.__active is not None:
            active = self.__entries[self.__active]
            oindex = 0
            def _print(_text:str):
                nonlocal self, oindex
                _rest = min(len(self._chars) - oindex, self._chars.width)
                for _i in range(min(len(_text), _rest)):
                    self._chars[oindex] = _boacon.BCChar(ord(_text[_i]))
                    oindex += 1
                    _rest -= 1
                while _rest > 0:
                    self._chars[oindex] = _SPACE
                    oindex += 1
                    _rest -= 1
            def _print_space():
                nonlocal self, oindex
                for _i in range(min(len(self._chars) - oindex, self._chars.width)):
                    self._chars[oindex] = _SPACE
                    oindex += 1
            # Name
            _print(f" {self.__active}")
            _print_space()
            # Current
            _print_space()
            _print(" Current:")
            _print(f" {self.__dtformat.create(active.curr_date)}")
            _print(f" {active.curr_price}")
            # Previous
            _print_space()
            _print(" Previous:")
            _print(" -" if (active.prev_price is None) else f" {self.__dtformat.create(active.prev_date)}")
            _print(" -" if (active.prev_price is None) else f" {active.prev_price}")
            # Fill rest
            if oindex < len(self._chars):
                self._chars[oindex] = _SPACE
                oindex += 1
        else: self._chars.clear

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)

    def _activated(self):
        super()._activated()

    def _deactivated(self):
        super()._deactivated()

    #endregion
all = ['StatusTable']

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

from .c_CryptoStats import\
    CryptoStats as _CryptoStats

_WIDTH_CURSOR = 3
_WIDTH_SYMBOL = 10
_WIDTH_PRICE = 20
_HEADER = _boacon.BCStr((\
    _boacon.BCStr(' ' * _WIDTH_CURSOR),\
    _boacon.BCStr("Symbol".ljust(_WIDTH_SYMBOL)),\
    _boacon.BCStr("Price".ljust(_WIDTH_PRICE))))

class StatusTable(_app.AppPaneObject):
    """
    Represents a table displaying the current status of currencies
    """

    #region init

    def __init__(self, crypto:_CryptoStats):
        """
        Initializer for StatusTable

        :params crypto:
            CryptoStats handler
        """
        super().__init__()
        # Recieve signals
        self.__crypto = crypto
        self.__crypto.newstats.connect(self.__r_newstats)

    #endregion

    #region receivers

    def __r_newstats(self):
        self._update_chrs()

    #endregion

    #region AppObjectPane
    
    def _refreshbuffer(self):
        super()._refreshbuffer()
        _SPACE = _boacon.BCChar(0x20)
        # Draw header
        for _i in range(min(len(_HEADER), self._chrs_w)):
            self._chrs[_i] = _HEADER[_i]
        # Draw rows
        for _i in range(len(self.__crypto.stats)):
            _stat = self.__crypto.stats[_i]
            _w = self._chrs_w
            _j = (_i + 1) * self._chrs_w
            # Cursor
            for _k in range(min(_WIDTH_CURSOR, _w)):
                self._chrs[_j] = _SPACE
                _w -= 1
                _j += 1
            # Symbol
            _s = _stat.currency.ljust(_WIDTH_SYMBOL)
            for _k in range(min(_WIDTH_SYMBOL, _w)):
                self._chrs[_j] = _boacon.BCChar(ord(_s[_k]))
                _w -= 1
                _j += 1
            # Price
            _s = str(_stat.price).ljust(_WIDTH_PRICE)
            for _k in range(min(_WIDTH_PRICE, _w)):
                self._chrs[_j] = _boacon.BCChar(ord(_s[_k]))
                _w -= 1
                _j += 1
            # Padding
            while _w > 0:
                self._chrs[_j] = _SPACE
                _w -= 1
                _j += 1

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)

    def _activated(self):
        super()._activated()

    def _deactivated(self):
        super()._deactivated()

    #endregion

    #region BCPane
    
    def _resolved(self):
        super()._resolved()

    def _draw(self,\
            setchr:_Callable[[int, int, _boacon.BCChar], None]):
        super()._draw(setchr)
        
    #endregion
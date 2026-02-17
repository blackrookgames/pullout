all = ['StatusTable']

import math as _math

from collections.abc import\
    Iterable as _Iterable
from typing import\
    Callable as _Callable,\
    cast as _cast

import engine.app as _app
import engine.boacon as _boacon
import engine.coroutine as _coroutine
import engine.cry as _cry
import engine.helper as _helper

from .c_CryptoStats import\
    CryptoStats as _Crypto

class StatusTable(_app.AppPaneObject):
    """
    Represents a table displaying the current status of currencies
    """

    #region init

    def __init__(self, crypto:_Crypto):
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
        for _stat in self.__crypto.stats:
            _app.console().print(f"{_stat.currency} {_stat.price}")

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
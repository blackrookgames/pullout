all = ['BuySell']

import curses as _curses

from typing import\
    Callable as _Callable,\
    cast as _cast

import engine.app as _app
import engine.boacon as _boacon

from .c_CryptoSignal import\
    CryptoSignal as _CryptoSignal
from .c_CryptoSignalEmitter import\
    CryptoSignalEmitter as _CryptoSignalEmitter
from .c_CryptoStats import\
    CryptoStats as _CryptoStats

class BuySell(_app.AppPaneObject):
    """
    Represents a handler for buying/selling
    """

    #region init

    def __init__(self,\
            crypto:_CryptoStats):
        """
        Initializer for BuySell

        :params crypto:
            CryptoStats handler
        """
        super().__init__()

    #endregion

    #region AppObjectPane
    
    def _refreshbuffer(self):
        super()._refreshbuffer()

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

    def _draw(self, setchr:_Callable[[int, int, _boacon.BCChar], None]):
        super()._draw(setchr)
        
    #endregion
all = ['BuySell']

import curses as _curses

from typing import\
    Callable as _Callable,\
    cast as _cast

import cry as _cry
import engine.app as _app
import engine.boacon as _boacon

from .c_CryptoKeeper import\
    CryptoKeeper as _CryptoKeeper

class BuySell(_app.AppPaneObject):
    """
    Represents a handler for buying/selling
    """

    #region init

    def __init__(self,\
            opparams:_cry.CryOpParams,\
            keeper:_CryptoKeeper):
        """
        Initializer for BuySell

        :params keeper:
            Crypto keeper
        """
        super().__init__()
        # Operation parameters
        self.__opparams = opparams
        # Stats handler 
        self.__keeper = keeper
        self.__keeper.refreshed.connect(self.__r_keeper_refreshed)

    #endregion

    #region receivers

    def __r_keeper_refreshed(self):
        pass

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
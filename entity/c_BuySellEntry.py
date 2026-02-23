all = ['BuySellEntry']

import curses as _curses

from datetime import\
    datetime as _datetime
from typing import\
    Callable as _Callable,\
    cast as _cast

import cry as _cry
import engine.app as _app
import engine.boacon as _boacon
import engine.helper as _helper

from .c_CryptoKeeper import\
    CryptoKeeper as _CryptoKeeper

class BuySellEntry:
    """
    Represents an entry within a buy/sell object
    """

    #region init

    def __init__(self,\
            crypto:_cry.Cry,\
            opparams:_cry.CryOpParams,\
            keeper:_CryptoKeeper,\
            name:str):
        """
        Initializer for BuySellEntry

        :params crypto:
            Crypto operation handler
        :params opparams:
            Parameters for Crypto-related operations
        :params keeper:
            Crypto keeper
        :params name:
            Name of crypto
        """
        super().__init__()
        # Crypto operation handler
        self.__crypto = crypto
        self.__opparams = opparams
        # Crypto keeper
        self.__keeper = keeper
        # Name
        self.__name = name
        # Initial values
        self.__first = True
        self.__when = self.__keeper.refreshed_when
        self.__price = 0.0
        self.__balance = 0.0
        self.__priceinc:None|float = None
        self.__compromised = False

    #endregion

    #region properties

    @property
    def name(self):
        """
        Crypto name
        """
        return self.__name

    @property
    def when(self):
        """
        Date and time of the last update
        """
        return self.__when

    @property
    def price(self):
        """
        Crypto price
        """
        return self.__price

    @property
    def balance(self):
        """
        Crypto balance
        """
        return self.__balance

    @property
    def compromised(self):
        """
        Whether or not integrity has been compromised
        """
        return self.__compromised
    
    @property
    def priceinc(self):
        """
        Increase (or decrease) in price. This value is None until the second update.
        """
        return self.__priceinc

    #endregion

    #region helper methods

    def _update(self):
        """
        Also accessed by BuySell
        """
        # Make sure this hasn't been compromised
        if self.__compromised: return
        # Update
        if self.__first:
            # Make sure crypto can be retrieved
            if not (self.__name in self.__keeper.prices):
                return
            # Get price and balance
            self.__when = self.__keeper.refreshed_when
            self.__price = self.__keeper.prices[self.__name].value
            self.__balance = self.__keeper.balances[self.__name].value
            # Next update will obviously not be the first update
            self.__first = False
        else:
            # Make sure crypto can be retrieved
            if not (self.__name in self.__keeper.prices):
                self.__compromised = True
                return
            # Previous price and balance
            prev_when = self.__when
            prev_price = self.__price
            prev_balance = self.__balance
            # Current price and balance
            self.__when = self.__keeper.refreshed_when
            self.__price = self.__keeper.prices[self.__name].value
            self.__balance = self.__keeper.balances[self.__name].value
            # Compare
            self.__priceinc = self.__price - prev_price

    def __print(self, text:str):
        if self.__opparams.printfunc is not None:
            self.__opparams.printfunc(text)
        else:
            _app.console().print(text)

    #endregion
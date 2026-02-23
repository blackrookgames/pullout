all = ['CryptoKeeper']

import math as _math

from datetime import\
    datetime as _datetime
from typing import\
    cast as _cast

import cry as _cry
import engine.app as _app
import engine.coroutine as _coroutine
import engine.helper as _helper

from .c_CryptoKeeperList import\
    CryptoKeeperList as _CryptoKeeperList
from .c_CryptoKeeperListAccess import\
    CryptoKeeperListAccess as _CryptoKeeperListAccess

class CryptoKeeper(_app.AppObject):
    """
    Represents an object that keeps up to date with crypto information
    """
    
    #region init

    def __init__(self,\
            crypto:_cry.Cry,\
            crypto_opparams:_cry.CryOpParams,\
            cryptocurrs:set[str],\
            noncrypto:str,\
            interval:float):
        """
        Initializer for CryptoKeeper
        
        :param crypto:
            Handler for crypto operations
        :param crypto_opparams:
            Parameters for crypto operations
        :param cryptocurrs:
            Crypto currencies to invest in (ex: BTC)
        :param noncrypto:
            Non-crypto currency to use for buying and selling
        :param interval:
            Length of update intervals
        """
        super().__init__()
        # Gather parameters
        self.__crypto = crypto
        self.__crypto_opparams = crypto_opparams
        self.__cryptocurrs = [_curr for _curr in cryptocurrs]
        # Initialize non-crypto
        self.__noncrypto = noncrypto
        self.__noncrypto_balance = 0.0
        # Initialize prices
        self.__prices_l = _CryptoKeeperListAccess[float]()
        self.__prices = _CryptoKeeperList[float](self.__prices_l)
        for _curr in self.__cryptocurrs: self.__prices_l.add(_curr, 0.0)
        # Initialize balances
        self.__balances_l = _CryptoKeeperListAccess[float]()
        self.__balances = _CryptoKeeperList[float](self.__balances_l)
        for _curr in self.__cryptocurrs: self.__balances_l.add(_curr, 0.0)
        # Initialize refresh info
        self.__refreshing = False
        self.__refreshed_when = _datetime(1990, 1, 1)
        self.__refreshed_e = _helper.SignalEmitter()
        self.__refreshed = _helper.Signal(self.__refreshed_e)
        # Initialize timer
        self.__interval = interval
        self.__timer = 0.0

    #endregion

    #region properties/signals

    @property
    def noncrypto(self):
        """
        Non-crypto currency to use for buying and selling
        """
        return self.__noncrypto

    @property
    def noncrypto_balance(self):
        """
        Balance of non-crypto currency
        """
        return self.__noncrypto_balance

    @property
    def prices(self):
        """
        Prices of each currency
        """
        return self.__prices

    @property
    def balances(self):
        """
        Balances of each currency
        """
        return self.__balances
    
    @property
    def refreshed_when(self):
        """
        Date/time information was refreshed
        """
        return self.__refreshed_when
    
    @property
    def refreshed(self):
        """
        Emitted after information has been refreshed
        """
        return self.__refreshed

    #endregion

    #region coroutines

    def __refresh(self):
        # Begin refreshing
        self.__refreshing = True
        # Retrieve prices
        new_prices = []
        _ptr = _helper.Ptr[float]()
        for _curr in self.__cryptocurrs:
            _task = self.__crypto.get_price_cr(f"{_curr}/{self.__noncrypto}", _ptr,\
                opparams = self.__crypto_opparams)
            for _yield in _task: yield _yield
            new_prices.append(_ptr.value)
        # Retrieve balance
        _ptr = _helper.Ptr[dict]()
        _task = self.__crypto.fetch_balance_cr(_ptr,\
            opparams = self.__crypto_opparams)
        for _yield in _task: yield _yield
        new_balance = _cast(dict, _ptr.value)["free"]
        # Refresh prices and balances
        for _i in range(len(self.__cryptocurrs)):
            _curr = self.__cryptocurrs[_i]
            # Refresh price
            self.__prices_l[_i] = new_prices[_i]
            # Refresh balance
            self.__balances_l[_i] = new_balance[_curr] if (_curr in new_balance) else 0.0
        # Refresh noncrypto balance
        self.__noncrypto_balance = new_balance[self.__noncrypto]\
            if (self.__noncrypto in new_balance) else 0.0
        # Success!!!
        self.__refreshed_when = _datetime.now()
        self.__refreshing = False
        self.__refreshed_e.emit()

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)
        # Update timer
        self.__timer += params.delta
        if self.__timer >= self.__interval:
            # Refresh
            if not self.__refreshing:
                _coroutine.create(self.__refresh())
            # "Reset" timer
            if self.__interval > 0.0:
                self.__timer -= _math.floor(self.__timer / self.__interval) * self.__interval
            else: self.__timer = 0.0

    def _activated(self):
        super()._activated()
        # First update
        _coroutine.create(self.__refresh())

    def _deactivated(self):
        super()._deactivated()

    #endregion
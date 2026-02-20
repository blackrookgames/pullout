all = ['CryptoStats']

import math as _math

from collections.abc import\
    Iterable as _Iterable
from datetime import\
    datetime as _datetime
from typing import\
    Callable as _Callable,\
    cast as _cast

import cry as _cry
import engine.app as _app
import engine.boacon as _boacon
import engine.coroutine as _coroutine
import engine.helper as _helper

from .c_CryptoStat import\
    CryptoStat as _CryptoStat

class CryptoStats(_app.AppObject):
    """
    Represents a handler for crypto stats
    """
    
    #region init

    def __init__(self,\
            crypto:_cry.Cry,\
            crypto_opparams:_cry.CryOpParams,\
            cryptocurrs:set[str],\
            noncrypto:str,\
            interval:float):
        """
        Initializer for CryptoStats
        
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
        self.__noncrypto = noncrypto
        self.__interval = interval
        # Initialize signals
        self.__newstats_e = _helper.SignalEmitter()
        self.__newstats = _helper.Signal(self.__newstats_e)
        # Initialize timer
        self.__timer = 0.0
        # Initialize stats
        self.__stats_list = [_CryptoStat(_curr) for _curr in self.__cryptocurrs]
        self.__stats = _helper.LockedList[_CryptoStat](self.__stats_list)
        self.__stats_updating = False
        self.__stats_updated = _datetime(1990, 1, 1)

    #endregion

    #region properties

    @property
    def stats(self):
        """
        Stats of each currency
        """
        return self.__stats
    
    @property
    def stats_updated(self):
        """
        Date/time stats were last updated
        """
        return self.__stats_updated

    #endregion

    #region signals

    @property
    def newstats(self):
        """
        Emitted when the CryptoStats stats are updated
        """
        return self.__newstats

    #endregion

    #region coroutines

    def __stats_update(self):
        self.__stats_updating = True
        # Get new stats
        prices = []
        for _curr in self.__cryptocurrs:
            _task_result = _helper.Ptr[float]()
            _task = self.__crypto.get_price_cr(\
                f"{_curr}/{self.__noncrypto}", _task_result, self.__crypto_opparams)
            for _yield in _task: yield _yield
            prices.append(_task_result.value)
        # Update stats
        for _i in range(len(self.__stats_list)):
            self.__stats_list[_i]._update(prices[_i])
        self.__stats_updated = _datetime.now()
        # Success!!!
        self.__stats_updating = False
        self.__newstats_e.emit()

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)
        # Update timer
        self.__timer += params.delta
        if self.__timer >= self.__interval:
            # Update stats
            if not self.__stats_updating:
                _coroutine.create(self.__stats_update())
            # "Reset" timer
            if self.__interval > 0.0:
                self.__timer -= _math.floor(self.__timer / self.__interval) * self.__interval
            else: self.__timer = 0.0

    def _activated(self):
        super()._activated()
        # First update
        _coroutine.create(self.__stats_update())

    def _deactivated(self):
        super()._deactivated()

    #endregion
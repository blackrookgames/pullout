all = ['CryptoStats']

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

from .c_CryptoSignal import\
    CryptoSignal as _CryptoSignal
from .c_CryptoSignalEmitter import\
    CryptoSignalEmitter as _CryptoSignalEmitter
from .c_CryptoStat import\
    CryptoStat as _CryptoStat

class CryptoStats(_app.AppObject):
    """
    Represents a handler for crypto stats
    """

    #region nested

    class __TaskCreator:
        def __init__(self, method, *args, **kwargs):
            """
            Assume
            - method returns cry.CryTask
            """
            self.__method = method
            self.__args = args
            self.__kwargs = kwargs
        def create(self):
            task = self.__method(*self.__args, **self.__kwargs)
            return _cast(_cry.CryTask, task)

    #endregion
    
    #region init

    def __init__(self,\
            symbols:dict[str, str], interval:float,\
            ddos_delay:float, ddos_max:int,\
            net_delay:float, net_max:int):
        """
        Initializer for CryptoStats
        
        :param symbols: Symbols (ex: BTC/USD)
        :param interval: Length of update intervals
        :param ddos_delay: Delay after DDOS error
        :param ddos_max: Max retries after DDOS error
        :param net_delay: Delay after network error
        :param net_max: Max retries after network error
        """
        super().__init__()
        # Gather parameters
        self.__symbols = { _k: _v for _k, _v in symbols.items() }
        self.__interval = interval
        self.__ddos_delay = ddos_delay
        self.__ddos_max = ddos_max
        self.__net_delay = net_delay
        self.__net_max = net_max
        # Initialize signals
        self.__newstats_e = _CryptoSignalEmitter()
        self.__newstats = _CryptoSignal(self.__newstats_e)
        # Initialize timer
        self.__timer = 0.0
        # Initialize market
        self.__market_loaded = False
        # Initialize stats
        self.__stats_list = [\
            _CryptoStat(_key) for _key in symbols]
        self.__stats = _helper.LockedList[_CryptoStat](self.__stats_list)
        self.__stats_updating = False

    #endregion

    #region properties

    @property
    def stats(self):
        """
        Stats of each currency
        """
        return self.__stats

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

    def __runtasks(self,\
            taskcreators:_Iterable[__TaskCreator],\
            tasks:list[_cry.CryTask]):
        def _retrymsg(\
                _msg:str,\
                _delay:float,\
                _retry:int,\
                _maxretries:int):
            return f"{_msg} Retrying in {_delay} seconds. {_retry}/{_maxretries}"
        tasks.clear()
        for _taskcreator in taskcreators:
            _ddos_retries = 0
            _net_retries = 0
            while True:
                # Run task
                _task = _taskcreator.create()
                _cry.queuetask(_task)
                yield _cry.CryTaskWait(_task)
                # Check task status
                if _task.status == _cry.CryTaskStatus.SUCCESS:
                    tasks.append(_task)
                    break
                assert _task.error is not None
                # DDOS protection?
                if _task.error.etype == _helper.CLIErrorType.DDOS:
                    if _ddos_retries >= self.__ddos_max:
                        raise _task.error
                    _ddos_retries += 1
                    _app.console().print(_retrymsg(\
                        "DDOS protection error",\
                        self.__ddos_delay,\
                        _ddos_retries,\
                        self.__ddos_max))
                    yield _coroutine.CRWaitTime(self.__ddos_delay)
                    continue
                # Network error?
                if _task.error.etype == _helper.CLIErrorType.NETWORK:
                    if _net_retries >= self.__net_max:
                        raise _task.error
                    _net_retries += 1
                    _app.console().print(_retrymsg(\
                        "Network error",\
                        self.__net_delay,\
                        _net_retries,\
                        self.__net_max))
                    yield _coroutine.CRWaitTime(self.__net_delay)
                    continue
                # Unexpected?
                raise _task.error

    def __market_load(self):
        _app.console().print("Loading markets")
        # Load markets
        creator = self.__TaskCreator(\
            lambda: _cry.CryTaskLoad())
        tasks = []
        for _wait in self.__runtasks([creator,], tasks):
            yield _wait
        # Success!!!
        self.__market_loaded = True
        _app.console().print("Markets loaded")

    def __stats_update(self):
        self.__stats_updating = True
        # Get new stats
        creators = [\
            self.__TaskCreator(\
                lambda _symbol: _cry.CryTaskPrice(_symbol),\
                f"{_key}/{_value}")\
            for _key, _value in self.__symbols.items()]
        tasks = []
        for _wait in self.__runtasks(creators, tasks):
            yield _wait
        for _i in range(len(self.__stats_list)):
            _task = _cast(_cry.CryTaskPrice, tasks[_i])
            self.__stats_list[_i]._update(_task.price)
        # Success!!!
        self.__stats_updating = False
        self.__newstats_e.emit()

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)
        # Make sure markets have loaded
        if not self.__market_loaded: return
        # Update timer
        self.__timer += params.delta
        if self.__timer >= self.__interval:
            # Update stats
            if not self.__stats_updating:
                _coroutine.create(self.__stats_update())
            # "Reset" timer
            if self.__interval > 0.0:
                self.__timer -=\
                    _math.floor(self.__timer / self.__interval)\
                    * self.__interval
            else: self.__timer = 0.0

    def _activated(self):
        super()._activated()
        # Load markets
        _coroutine.create(self.__market_load())

    def _deactivated(self):
        super()._deactivated()

    #endregion
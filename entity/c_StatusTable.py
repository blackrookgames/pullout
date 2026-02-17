all = ['StatTable']

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

class StatusTable(_app.AppPaneObject):
    """
    Represents a table displaying the current status of currencies
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
        Initializer for StatusTable
        
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
        # Initialize timer
        self.__timer = 0.0
        # Initialize markets
        self.__loaded = False
        # Initialize fetch state
        self.__fetching = False

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

    def __load(self):
        _app.console().print("Loading markets")
        # Load markets
        creator = self.__TaskCreator(\
            lambda: _cry.CryTaskLoad())
        tasks = []
        for _wait in self.__runtasks([creator,], tasks):
            yield _wait
        # Success!!!
        self.__loaded = True
        _app.console().print("Markets loaded")

    def __fetch(self):
        # Mark as fetching
        self.__fetching = True
        # Fetch from market
        creators = [\
            self.__TaskCreator(\
                lambda _symbol: _cry.CryTaskPrice(_symbol),\
                f"{_key}/{_value}")\
            for _key, _value in self.__symbols.items()]
        tasks = []
        for _wait in self.__runtasks(creators, tasks):
            yield _wait
        for _task in tasks:
            assert isinstance(_task, _cry.CryTaskPrice)
            _app.console().print(f"{_task.symbol} {_task.price}")
        # Mark as not fetching
        self.__fetching = False

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)
        # Make sure markets have loaded
        if not self.__loaded: return
        # Update timer
        self.__timer += params.delta
        if self.__timer >= self.__interval:
            # Fetch
            if not self.__fetching:
                _coroutine.create(self.__fetch())
            # Test
            _app.console().print("Interval")
            # "Reset" timer
            if self.__interval > 0.0:
                self.__timer -=\
                    _math.floor(self.__timer / self.__interval)\
                    * self.__interval
            else: self.__timer = 0.0

    def _activated(self):
        super()._activated()
        # Load markets
        _coroutine.create(self.__load())

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
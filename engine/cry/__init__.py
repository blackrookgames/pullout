from .c_CryTask import *
from .c_CryTaskBalance import *
from .c_CryTaskLoad import *
from .c_CryTaskPrice import *
from .c_CryTaskStatus import *
from .c_CryTaskWait import *

import asyncio as _asyncio
import ccxt as _ccxt

from typing import\
    Any as _Any,\
    cast as _cast

from ..helper.c_CLIError import\
    CLIError as _CLIError
from ..helper.c_State import\
    State as _State
from .c__CryAPI import _CryAPI

#region variables

_f_state:_State = _State.NOTRUN
_f_exchange:None|_ccxt.coinbase = None
_f_tasks:list[CryTask] = []

#endregion

#region init/final/update

def _m_init(apipath:_Any):
    """
    Also accessed by ../app/__init__.py

    :raise CLIError:
        An error occurred
    """
    global _f_state
    if _f_state != _State.NOTRUN: return
    _f_state = _State.INIT
    # Access exchange
    def _exchange():
        nonlocal apipath
        try:
            # Create exchange instance
            _api = _CryAPI(apipath)
            _exchange = _ccxt.coinbase({ \
                'apiKey': _api.key, \
                'secret': _api.secret, \
                'enableRateLimit': True, })
            # Setup options
            if not isinstance(_exchange.options, dict):
                raise _CLIError("Failed to create interface.")
            option = 'createMarketSellOrderRequiresPrice'
            _exchange.options[option] = 'False' # type: ignore
            option = 'createMarketBuyOrderRequiresPrice'
            _exchange.options[option] = 'False' # type: ignore
            # Success!!!
            return _exchange
        except _CLIError as _e:
            e = _e
        except Exception as _e:
            e = _CLIError(_e)
        raise e
    global _f_exchange
    _f_exchange = _exchange()
    # Initialize tasks
    global _f_tasks
    _f_tasks = []
    # Success!!!
    _f_state = _State.RUN

def _m_final():
    """
    Also accessed by ../app/__init__.py
    """
    global _f_state
    if _f_state != _State.RUN: return
    _f_state = _State.FINAL
    # Success!!!
    _f_state = _State.NOTRUN

async def _m_update(loop:_asyncio.AbstractEventLoop):
    """
    Assume
    - _m_state == _State.RUN
    \n
    Also accessed by ../app/__init__.py
    """
    global _f_exchange, f_tasks
    assert _f_exchange is not None
    # Update tasks
    if len(_f_tasks) > 0:
        _task = _f_tasks[0]
        if _task.status == CryTaskStatus.INIT:
            _task = loop.run_in_executor(None, _task._run, _f_exchange)
            async def _runtask(): await _task
            _asyncio.create_task(_runtask())
        elif not _task.stillrunning():
            _f_tasks.pop(0)

#endregion

#region "properties"

def state():
    """
    State of the crypto access handler
    """
    global _f_state
    return _f_state

#endregion

#region methods

def queuetask(task:CryTask):
    """
    Queues a task to be executed; 
    if the task has already been executed, nothing happens

    :param task:
        Task to run
    :raise BadOpError:
        Crypto access handler is not currently running
    """
    global _f_state
    _f_state.raise_if_notrunning("Crypto access handler")
    if task.status != CryTaskStatus.INIT: return
    _f_tasks.append(task)

#endregion
from .c_ACRTask import *
from .c_ACRTaskStatus import *
from .c_ACRTaskWait import *

import asyncio as _asyncio

from typing import\
    Any as _Any,\
    cast as _cast

from ..helper.c_CLIError import\
    CLIError as _CLIError
from ..helper.c_State import\
    State as _State

#region variables

_f_state:_State = _State.NOTRUN
_f_tasks:list[ACRTask] = []

#endregion

#region init/final/update

def _m_init():
    """
    Also accessed by ../app/__init__.py

    :raise CLIError:
        An error occurred
    """
    global _f_state
    if _f_state != _State.NOTRUN: return
    _f_state = _State.INIT
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
    global f_tasks
    # Update tasks
    if len(_f_tasks) > 0:
        _task = _f_tasks[0]
        if _task.status == ACRTaskStatus.INIT:
            _task = loop.run_in_executor(None, _task._run)
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

def queuetask(task:ACRTask):
    """
    Queues a task to be executed; 
    if the task has already been executed, nothing happens

    :param task:
        Task to run
    :raise BadOpError:
        Async task handler is not currently running
    """
    global _f_state
    _f_state.raise_if_notrunning("Async task handler")
    if task.status != ACRTaskStatus.INIT: return
    _f_tasks.append(task)

#endregion
from .c_CRGen import *
from .c_CRWait import *
from .c_CRWaitTime import *
from .c_CRWaitWhile import *

from ..helper.c_State import\
    State as _State
from .c__CRCoroutine import _CRCoroutine

#region variables

_f_state:_State = _State.NOTRUN
_f_coroutines:list[_CRCoroutine] = []

#endregion

#region init/final/update

def _m_init():
    """
    Also accessed by ../app/__init__.py
    """
    global _f_state
    if _f_state != _State.NOTRUN: return
    _f_state = _State.INIT
    # Initialize coroutines
    global _f_coroutines
    _f_coroutines = []
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

def _m_update(delta:float):
    """
    Assume
    - _m_state == _State.RUN
    - delta >= 0.0
    \n
    Also accessed by ../app/__init__.py
    """
    global _f_coroutines
    _i = 0
    while _i < len(_f_coroutines):
        _cr = _f_coroutines[_i]
        _cr._update(delta)
        if _cr.finish: _f_coroutines.pop(_i)
        else: _i += 1

#endregion

#region "properties"

def state():
    """
    State of the coroutine system
    """
    global _f_state
    return _f_state

#endregion

#region methods

def create(generator:CRGen):
    """
    Creates a new coroutine

    :param generator:
        Generator for coroutine
    :raise BadOpError:
        Coroutine system is not currently running
    """
    global _f_state
    _f_state.raise_if_notrunning("Coroutine system")
    global _f_coroutines
    _f_coroutines.append(_CRCoroutine(generator))
    
#endregion
from .c_AppObject import *
from .c_AppStart import *
from .c_AppUpdate import *

import asyncio

import src.boacon as _boacon
import src.coroutine as _coroutine
import src.cry as _cry
import src.helper as _helper

#region variables

_f_running = False
_f_console = _boacon.BCConsolePane()

_f_looping = False
_f_objects:list[AppObject] = []

#endregion

#region helper methods

async def _m_main():
    loop = asyncio.get_running_loop()
    time = loop.time()
    while _f_looping:
        # Get keyboard input
        _key = _boacon.getch()
        if _key == 0x1B: break
        # Update time
        _time = time
        time = loop.time()
        _delta = time - _time
        # Update subsystems
        _coroutine._m_update(_delta)
        await _cry._m_update(loop)
        # Update objects
        _update = AppUpdate(_delta, _key)
        for _obj in _f_objects:
            _obj._update(_update)
        # Refresh boacon
        _boacon.refresh()
        # Next
        await asyncio.sleep(0.05)

def _m_raise_if_notrunning():
    global _f_running
    if _f_running: return
    raise _helper.BadOpError(
        "Main application handler is not currently running.")

#endregion

#region "properties"

def running():
    """
    Whether or not the application handler is running
    """
    global _f_running
    return _f_running

def console():
    """
    Console pane
    """
    global _f_console
    return _f_console

#endregion

#region methods

def run(params:AppStart):
    """
    Executes the main application code

    :param params:
        Parameters for starting the main application code
    :raise CLIError:
        An error occurred
    """
    global _f_running, _f_console, _f_looping, _f_objects
    if _f_running: return
    try:
        # Mark as running
        _f_running = True
        # Reset looping
        _f_looping = True
        # Add objects
        _f_objects = [_obj for _obj in params.objects]
        for _obj in _f_objects: _obj._set_active(True)
        # Initialize subsystems
        _coroutine._m_init()
        _cry._m_init(params.apipath)
        # Initialize boacon
        _boacon.init()
        _boacon.panes().append(_f_console)
        _f_console.x.dis0 = 1
        _f_console.x.dis1 = 1
        _f_console.x.len = None
        _f_console.y.dis0 = 3
        _f_console.y.dis1 = 1
        _f_console.y.len = None
        # Run async
        asyncio.run(_m_main())
        # Success!!!
        return
    except _helper.CLIError as _e:
        e = _e
    finally:
        # Finalize boacon
        _boacon.final()
        # Finalize subsystems
        _cry._m_final()
        _coroutine._m_final()
        # Remove objects
        for _obj in _f_objects: _obj._set_active(False)
        _f_objects.clear()
        # Mark as not running
        _f_running = False
    raise e

def object_add(obj:AppObject):
    """
    Adds the specified object to the update pool, making it active. 
    If object is already part of the update pool, nothing happens.

    :param obj:
        Object to add
    :raise BadOpError:
        Main application handler is not currently running
    """
    _m_raise_if_notrunning()
    if obj.active: return
    global _f_objects
    _f_objects.append(obj)
    obj._set_active(True)

def object_remove(obj:AppObject):
    """
    Removes the specified object from the update pool, making it inactive. 
    If object is not part of the update pool, nothing happens.

    :param obj:
        Object to remove
    :raise BadOpError:
        Main application handler is not currently running
    """
    _m_raise_if_notrunning()
    if not obj.active: return
    global _f_objects
    _f_objects.remove(obj)
    obj._set_active(False)

#endregion
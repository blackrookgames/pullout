from .c_AppObject import *
from .c_AppPaneObject import *
from .c_AppPaneObjectCharBuffer import *
from .c_AppStart import *
from .c_AppUpdate import *

import asyncio

import engine.asynccr as _asynccr
import engine.boacon as _boacon
import engine.coroutine as _coroutine
import engine.helper as _helper

#region variables

_f_running = False
_f_console = _boacon.BCConsolePane()

_f_looping = False
_f_objects:list[AppObject] = []
_f_focused:None|AppObject = None

#endregion

#region helper methods

def _m_focus_set(focused:None|AppObject):
    global _f_focused
    if _f_focused is focused: return
    prev = _f_focused
    _f_focused = focused
    # Set states
    if prev is not None: prev._set_focus(False)
    if _f_focused is not None: _f_focused._set_focus(True)
    # Call methods
    if prev is not None: prev._focus_lost()
    if _f_focused is not None: _f_focused._focus_gained()

def _m_focus_update(exclude:None|AppObject):
    """
    Also accessed by AppObject
    """
    # Make sure we are running (just return if we're not)
    global _f_running
    if not _f_running: return
    # Check if focus needs to be updated
    global _f_focused
    if not (_f_focused is None or _f_focused is exclude or (not _f_focused.focusable)):
        return
    # Find an object to focus on
    global _f_objects
    found = None
    for _obj in _f_objects:
        if _obj is exclude: continue
        if not _obj.focusable: continue
        found = _obj
        break
    # Update focus
    _m_focus_set(found)

async def _m_main():
    # Welcome
    global _f_console
    _f_console.print("Written by Zachary Combs")
    # Loop
    global _f_objects, _f_focused
    loop = asyncio.get_running_loop()
    time = loop.time()
    while _f_looping:
        # Get keyboard input
        _key = _boacon.getch()
        if _key == 0x09:
            # Update focus
            if _f_focused is None:
                _m_focus_update(None)
            else:
                # Find index of object that's currently in focus
                _start = _f_objects.index(_f_focused)
                # Find next object
                _found = None
                for _i in range(len(_f_objects)):
                    _obj = _f_objects[(_start + 1 + _i) % len(_f_objects)]
                    if not _obj.focusable: continue
                    _found = _obj
                    break
                _m_focus_set(_found)
        # Update time
        _time = time
        time = loop.time()
        _delta = time - _time
        # Update subsystems
        _coroutine._m_update(_delta)
        await _asynccr._m_update(loop)
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
        # Initialize subsystems
        _coroutine._m_init()
        _asynccr._m_init()
        # Initialize boacon
        _boacon.init()
        _boacon.set_border(False)
        _boacon.panes().append(_f_console)
        _f_console.x.dis0 = params.con_left
        _f_console.x.dis1 = params.con_right
        _f_console.x.len = params.con_width
        _f_console.y.dis0 = params.con_top
        _f_console.y.dis1 = params.con_bottom
        _f_console.y.len = params.con_height
        # Add objects
        _f_objects = [_obj for _obj in params.objects]
        for _obj in _f_objects: _obj._set_active(True)
        # Set focus
        _m_focus_update(None)
        # Run async
        asyncio.run(_m_main())
        # Success!!!
        return
    except _helper.CLIError as _e:
        e = _e
    finally:
        # Remove objects
        for _obj in _f_objects: _obj._set_active(False)
        _f_objects.clear()
        # Finalize boacon
        _boacon.final()
        # Finalize subsystems
        _asynccr._m_final()
        _coroutine._m_final()
        # Mark as not running
        _f_running = False
    raise e

def quit():
    """
    Quits the application

    :raise BadOpError:
        Main application handler is not currently running
    """
    _m_raise_if_notrunning()
    global _f_looping
    _f_looping = False
    
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
    # Add object
    _f_objects.append(obj)
    # Set object as active
    obj._set_active(True)
    # Update focus
    _m_focus_update(None)

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
    global _f_objects, _f_focused
    # Update focus
    if obj is _f_focused:
        _m_focus_update(_f_focused)
    # Remove object
    _f_objects.remove(obj)
    # Set object as inactive
    obj._set_active(False)

#endregion
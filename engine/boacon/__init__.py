from .c_BCChar import *
from .c_BCCoord import *
from .c_BCError import *
from .c_BCPane import *
from .c_BCSignal import *
from .c_BCSignalEmitter import *
from .c_BCState import *
from .c_BCStr import *
from .g_attr import *
from .g_key import *
from .p_BCConsolePane import *

import curses as _curses
import numpy as _np
import numpy.typing as _npt

#region const

_C_BORDERCHARS = [\
    0xFF, 0x50, 0x50, 0x50, 0x51, 0x54, 0x5A, 0x50, 0x51, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x5D, 0x50, 0x69, 0x50, 0x51, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x5A, 0x50, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x51, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x69, 0x50, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x57, 0x66, 0x50, 0x50, 0x51, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x63, 0x66, 0x69, 0x50, 0x51, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x6C, 0x66, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x6C, 0x66, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x54, 0x66, 0x50, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x51, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x6C, 0x66, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x60, 0x66, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x51, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x6C, 0x66, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x66, 0x66, 0x50, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x6C, 0x66, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x6C, 0x66, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,\
    0x6C, 0x66, 0x69, 0x50, 0x60, 0x54, 0x5A, 0x50, 0x63, 0x57, 0x5D, 0x50, 0x51, 0x51, 0x51, 0xA1,]

#endregion

#region variables

_f_state = BCState.NORUN
_f_win:None|_curses.window = None
_f_win_ok = False
_f_win_w = 0
_f_win_h = 0
_f_color = False
_f_panes:None|list[BCPane] = None
_f_bgbuffer:None|_npt.NDArray[_np.bool_] = None

_f_border = False

_s_on_init_emitter = BCSignalEmitter[()]()
_s_on_init = BCSignal(_s_on_init_emitter)
_s_on_final_emitter = BCSignalEmitter[()]()
_s_on_final = BCSignal(_s_on_final_emitter)

_s_postdraw_emitter:None|BCSignalEmitter[_curses.window] = None
_s_postdraw:None|BCSignal[_curses.window] = None

#endregion

#region helper

def _m_verify_run():
    global _f_state
    if _f_state == BCState.RUN: return
    raise BCError("boacon system is not currently running.")

def _m_setcursor(visible:bool):
    global _f_win, _f_win_ok
    assert _f_win is not None
    # Try to hide normally
    if not _f_win_ok:
        try: _curses.curs_set(1 if visible else 0)
        except _curses.error: _f_win_ok = True
    # Try to hide alternatively
    if _f_win_ok: # Do NOT change to else or elif
        try: _f_win.leaveok(not visible)
        except _curses.error: pass

def _m_setchr_color(x:int, y:int, chr:BCChar):
    global _f_win, _f_bgbuffer, _f_win_w
    assert _f_win is not None
    assert _f_bgbuffer is not None
    attr = _curses.A_STANDOUT if attr_emp(chr.attr) else _curses.A_NORMAL
    attr |= _curses.color_pair(0b111 ^ attr_color(chr.attr))
    try:
        _f_win.addch(y, x, chr.ord, attr)
        _f_bgbuffer[y * _f_win_w + x] = True
    except: pass

def _m_setchr_nocolor(x:int, y:int, chr:BCChar):
    global _f_win, _f_bgbuffer, _f_win_w
    assert _f_win is not None
    assert _f_bgbuffer is not None
    attr = _curses.A_STANDOUT if attr_emp(chr.attr) else _curses.A_NORMAL
    try:
        _f_win.addch(y, x, chr.ord, attr)
        _f_bgbuffer[y * _f_win_w + x] = True
    except: pass

def _m_borderchar(x:int, y:int):
    global _f_win_w, _f_win_h, _f_bgbuffer
    assert _f_bgbuffer is not None
    # Examine neighbors
    index = y * _f_win_w + x
    index_t = index - _f_win_w
    index_b = index + _f_win_w
    notedge_t = y > 0
    notedge_b = (y + 1) < _f_win_h
    notedge_l = x > 0
    notedge_r = (x + 1) < _f_win_w
    if notedge_t:
        neighbor_t = _f_bgbuffer[index_t]
        neighbor_tl = notedge_l and _f_bgbuffer[index_t - 1]
        neighbor_tr = notedge_r and _f_bgbuffer[index_t + 1]
    else:
        neighbor_t = False
        neighbor_tl = False
        neighbor_tr = False
    if notedge_b:
        neighbor_b = _f_bgbuffer[index_b]
        neighbor_bl = notedge_l and _f_bgbuffer[index_b - 1]
        neighbor_br = notedge_r and _f_bgbuffer[index_b + 1]
    else:
        neighbor_b = False
        neighbor_bl = False
        neighbor_br = False
    neighbor_l = notedge_l and _f_bgbuffer[index - 1]
    neighbor_r = notedge_r and _f_bgbuffer[index + 1]
    # Determine character
    index = 0
    if neighbor_t: index |= 0b00000001
    if neighbor_b: index |= 0b00000010
    if neighbor_l: index |= 0b00000100
    if neighbor_r: index |= 0b00001000
    if neighbor_tl: index |= 0b00010000
    if neighbor_tr: index |= 0b00100000
    if neighbor_bl: index |= 0b01000000
    if neighbor_br: index |= 0b10000000
    raw = _C_BORDERCHARS[index]
    return ' ' if (raw == 0xFF) else chr(0x2500 | raw)

#endregion

#region init/final

def init():
    global _f_state
    if _f_state != BCState.NORUN: return
    _f_state = BCState.INIT
    # Global vars
    global _f_win, _f_win_w, _f_win_h, _f_color, _f_panes
    global _f_border
    # Initialize window
    _f_win = _curses.initscr()
    _f_win.keypad(True)
    _f_win.nodelay(True)
    _f_win_w = 0
    _f_win_h = 0
    # Initialize curses
    _curses.noecho()
    _curses.cbreak()
    _m_setcursor(False)
    # Initialize color
    _curses.start_color()
    if _curses.has_colors() and _curses.COLOR_PAIRS >= 8:
        _curses.use_default_colors()
        _curses.init_pair(0b001, _curses.COLOR_CYAN, -1)
        _curses.init_pair(0b010, _curses.COLOR_MAGENTA, -1)
        _curses.init_pair(0b011, _curses.COLOR_BLUE, -1)
        _curses.init_pair(0b100, _curses.COLOR_YELLOW, -1)
        _curses.init_pair(0b101, _curses.COLOR_GREEN, -1)
        _curses.init_pair(0b110, _curses.COLOR_RED, -1)
        _curses.init_pair(0b111, _curses.COLOR_BLACK, -1)
        _f_color = True
    else:
        _f_color = False
    # Initialize panes
    _f_panes = []
    # Initialize border
    _f_border = True
    # Initialize signals
    global _s_postdraw, _s_postdraw_emitter
    _s_postdraw_emitter = BCSignalEmitter[_curses.window]()
    _s_postdraw = BCSignal[_curses.window](_s_postdraw_emitter)
    # Success!!!
    _f_state = BCState.RUN
    _s_on_init_emitter.emit(())

def final():
    global _f_state
    if _f_state != BCState.RUN: return
    _s_on_final_emitter.emit(())
    _f_state = BCState.FINAL
    # Global vars
    global _f_win, _panes
    assert _f_win is not None
    # Finalize curses
    _curses.nocbreak()
    _curses.echo()
    _curses.endwin()
    # Finalize window
    _m_setcursor(True)
    _f_win.nodelay(False)
    _f_win.keypad(False)
    # Success!!!
    _f_state = BCState.NORUN

#endregion

#region "properties"

def state():
    """
    State of the boacon system
    """
    global _f_state
    return _f_state

def panes():
    """
    Panes that are being displayed
    
    :raise BCError:
        boacon system is not currently running
    """
    _m_verify_run()
    global _f_panes
    assert _f_panes is not None
    return _f_panes

def on_init():
    """
    Emitted after the boacon system is initialized
    """
    global _s_on_init
    return _s_on_init

def on_final():
    """
    Emitted before the boacon system is finalized
    """
    global _s_on_final
    return _s_on_final

def postdraw():
    """
    Emitted after drawing the panes and right before the screen is refreshed
    
    :raise BCError:
        boacon system is not currently running
    """
    _m_verify_run()
    global _s_postdraw
    assert _s_postdraw is not None
    return _s_postdraw

#endregion

#region functions

def refresh():
    """
    Refreshes the screen
    
    :raise BCError:
        boacon system is not currently running
    """
    _m_verify_run()
    global _f_win, _f_win_w, _f_win_h, _f_color, _f_panes, _f_bgbuffer
    global _f_border
    assert _f_win is not None
    assert _f_panes is not None
    global _s_postdraw_emitter
    assert _s_postdraw_emitter is not None
    # Update size
    _new_h, _new_w = _f_win.getmaxyx()
    if _f_win_w != _new_w or _f_win_h != _new_h:
        _f_win_w = _new_w
        _f_win_h = _new_h
        _f_bgbuffer = _np.zeros(_f_win_w * _f_win_h, dtype = bool)
        resized = True
    else:
        assert _f_bgbuffer is not None
        resized = False
    # Resolve pane dimensions
    redrawbg = resized
    for _pane in _f_panes:
        if _pane._m_resolve(resized, _f_win_w, _f_win_h):
            redrawbg = True
    if redrawbg:
        _f_bgbuffer.fill(False)
    # Update panes
    _setchr = _m_setchr_color if _f_color else _m_setchr_nocolor
    for _pane in _f_panes:
        _pane._m_refresh(redrawbg, _setchr)
    # Draw background
    if redrawbg:
        for _y in range(_f_win_h):
            for _x in range(_f_win_w):
                _i = _y * _f_win_w + _x
                if _f_bgbuffer[_i]: continue
                # Determine character
                _chr = _m_borderchar(_x, _y) if _f_border else ' '
                # Set character
                try: _f_win.addch(_y, _x, _chr)
                except: pass
    # Post draw
    _s_postdraw_emitter.emit((_f_win,))
    # Success!!!
    _f_win.refresh()
    
def getch():
    """
    Gets a character code from the keyboard
    
    :return:
        Character code (or -1 if no character is pressed)
    :raise BCError:
        boacon system is not currently running
    """
    _m_verify_run()
    global _f_win
    assert _f_win is not None
    return _f_win.getch()

def get_border():
    """
    Gets whether or not pane borders are enabled
    
    :raise BCError:
        boacon system is not currently running
    """
    _m_verify_run()
    global _f_border
    return _f_border

def set_border(value:bool):
    """
    Sets whether or not pane borders are enabled
    
    :raise BCError:
        boacon system is not currently running
    """
    _m_verify_run()
    global _f_border
    _f_border = value

#endregion
all = [\
    'key_min',\
    'key_break',\
    'key_down',\
    'key_up',\
    'key_left',\
    'key_right',\
    'key_home',\
    'key_backspace',\
    'key_f1',\
    'key_f2',\
    'key_f3',\
    'key_f4',\
    'key_f5',\
    'key_f6',\
    'key_f7',\
    'key_f8',\
    'key_f9',\
    'key_f10',\
    'key_f11',\
    'key_f12',\
    'key_dl',\
    'key_il',\
    'key_dc',\
    'key_ic',\
    'key_eic',\
    'key_clear',\
    'key_eos',\
    'key_eol',\
    'key_sf',\
    'key_sr',\
    'key_npage',\
    'key_ppage',\
    'key_stab',\
    'key_ctab',\
    'key_catab',\
    'key_enter',\
    'key_sreset',\
    'key_reset',\
    'key_print',\
    'key_ll',\
    'key_a1',\
    'key_a3',\
    'key_b2',\
    'key_c1',\
    'key_c3',\
    'key_btab',\
    'key_beg',\
    'key_cancel',\
    'key_close',\
    'key_command',\
    'key_copy',\
    'key_create',\
    'key_end',\
    'key_exit',\
    'key_find',\
    'key_help',\
    'key_mark',\
    'key_message',\
    'key_move',\
    'key_next',\
    'key_open',\
    'key_options',\
    'key_previous',\
    'key_redo',\
    'key_reference',\
    'key_refresh',\
    'key_replace',\
    'key_restart',\
    'key_resume',\
    'key_save',\
    'key_sbeg',\
    'key_scancel',\
    'key_scommand',\
    'key_scopy',\
    'key_screate',\
    'key_sdc',\
    'key_sdl',\
    'key_select',\
    'key_send',\
    'key_seol',\
    'key_sexit',\
    'key_sfind',\
    'key_shelp',\
    'key_shome',\
    'key_sic',\
    'key_sleft',\
    'key_smessage',\
    'key_smove',\
    'key_snext',\
    'key_soptions',\
    'key_sprevious',\
    'key_sprint',\
    'key_sredo',\
    'key_sreplace',\
    'key_sright',\
    'key_srsume',\
    'key_ssave',\
    'key_ssuspend',\
    'key_sundo',\
    'key_suspend',\
    'key_undo',\
    'key_mouse',\
    'key_resize',\
    'key_max',]

import curses as _curses

def key_min():
    """
    Minimum key value
    """
    return _curses.KEY_MIN

def key_break():
    """
    Break key (unreliable)
    """
    return _curses.KEY_BREAK

def key_down():
    """
    Down-arrow
    """
    return _curses.KEY_DOWN

def key_up():
    """
    Up-arrow
    """
    return _curses.KEY_UP

def key_left():
    """
    Left-arrow
    """
    return _curses.KEY_LEFT

def key_right():
    """
    Right-arrow
    """
    return _curses.KEY_RIGHT

def key_home():
    """
    Home key (upward+left arrow)
    """
    return _curses.KEY_HOME

def key_backspace():
    """
    Backspace (unreliable)
    """
    return _curses.KEY_BACKSPACE

def key_f1():
    """
    Value of function key 1
    """
    return _curses.KEY_F1

def key_f2():
    """
    Value of function key 2
    """
    return _curses.KEY_F2

def key_f3():
    """
    Value of function key 3
    """
    return _curses.KEY_F3

def key_f4():
    """
    Value of function key 4
    """
    return _curses.KEY_F4

def key_f5():
    """
    Value of function key 5
    """
    return _curses.KEY_F5

def key_f6():
    """
    Value of function key 6
    """
    return _curses.KEY_F6

def key_f7():
    """
    Value of function key 7
    """
    return _curses.KEY_F7

def key_f8():
    """
    Value of function key 8
    """
    return _curses.KEY_F8

def key_f9():
    """
    Value of function key 9
    """
    return _curses.KEY_F9

def key_f10():
    """
    Value of function key 10
    """
    return _curses.KEY_F10

def key_f11():
    """
    Value of function key 11
    """
    return _curses.KEY_F11

def key_f12():
    """
    Value of function key 12
    """
    return _curses.KEY_F12

def key_dl():
    """
    Delete line
    """
    return _curses.KEY_DL

def key_il():
    """
    Insert line
    """
    return _curses.KEY_IL

def key_dc():
    """
    Delete character
    """
    return _curses.KEY_DC

def key_ic():
    """
    Insert char or enter insert mode
    """
    return _curses.KEY_IC

def key_eic():
    """
    Exit insert char mode
    """
    return _curses.KEY_EIC

def key_clear():
    """
    Clear screen
    """
    return _curses.KEY_CLEAR

def key_eos():
    """
    Clear to end of screen
    """
    return _curses.KEY_EOS

def key_eol():
    """
    Clear to end of line
    """
    return _curses.KEY_EOL

def key_sf():
    """
    Scroll 1 line forward
    """
    return _curses.KEY_SF

def key_sr():
    """
    Scroll 1 line backward (reverse)
    """
    return _curses.KEY_SR

def key_npage():
    """
    Next page
    """
    return _curses.KEY_NPAGE

def key_ppage():
    """
    Previous page
    """
    return _curses.KEY_PPAGE

def key_stab():
    """
    Set tab
    """
    return _curses.KEY_STAB

def key_ctab():
    """
    Clear tab
    """
    return _curses.KEY_CTAB

def key_catab():
    """
    Clear all tabs
    """
    return _curses.KEY_CATAB

def key_enter():
    """
    Enter or send (unreliable)
    """
    return _curses.KEY_ENTER

def key_sreset():
    """
    Soft (partial) reset (unreliable)
    """
    return _curses.KEY_SRESET

def key_reset():
    """
    Reset or hard reset (unreliable)
    """
    return _curses.KEY_RESET

def key_print():
    """
    Print
    """
    return _curses.KEY_PRINT

def key_ll():
    """
    Home down or bottom (lower left)
    """
    return _curses.KEY_LL

def key_a1():
    """
    Upper left of keypad
    """
    return _curses.KEY_A1

def key_a3():
    """
    Upper right of keypad
    """
    return _curses.KEY_A3

def key_b2():
    """
    Center of keypad
    """
    return _curses.KEY_B2

def key_c1():
    """
    Lower left of keypad
    """
    return _curses.KEY_C1

def key_c3():
    """
    Lower right of keypad
    """
    return _curses.KEY_C3

def key_btab():
    """
    Back tab
    """
    return _curses.KEY_BTAB

def key_beg():
    """
    Beg (beginning)
    """
    return _curses.KEY_BEG

def key_cancel():
    """
    Cancel
    """
    return _curses.KEY_CANCEL

def key_close():
    """
    Close
    """
    return _curses.KEY_CLOSE

def key_command():
    """
    Cmd (command)
    """
    return _curses.KEY_COMMAND

def key_copy():
    """
    Copy
    """
    return _curses.KEY_COPY

def key_create():
    """
    Create
    """
    return _curses.KEY_CREATE

def key_end():
    """
    End
    """
    return _curses.KEY_END

def key_exit():
    """
    Exit
    """
    return _curses.KEY_EXIT

def key_find():
    """
    Find
    """
    return _curses.KEY_FIND

def key_help():
    """
    Help
    """
    return _curses.KEY_HELP

def key_mark():
    """
    Mark
    """
    return _curses.KEY_MARK

def key_message():
    """
    Message
    """
    return _curses.KEY_MESSAGE

def key_move():
    """
    Move
    """
    return _curses.KEY_MOVE

def key_next():
    """
    Next
    """
    return _curses.KEY_NEXT

def key_open():
    """
    Open
    """
    return _curses.KEY_OPEN

def key_options():
    """
    Options
    """
    return _curses.KEY_OPTIONS

def key_previous():
    """
    Prev (previous)
    """
    return _curses.KEY_PREVIOUS

def key_redo():
    """
    Redo
    """
    return _curses.KEY_REDO

def key_reference():
    """
    Ref (reference)
    """
    return _curses.KEY_REFERENCE

def key_refresh():
    """
    Refresh
    """
    return _curses.KEY_REFRESH

def key_replace():
    """
    Replace
    """
    return _curses.KEY_REPLACE

def key_restart():
    """
    Restart
    """
    return _curses.KEY_RESTART

def key_resume():
    """
    Resume
    """
    return _curses.KEY_RESUME

def key_save():
    """
    Save
    """
    return _curses.KEY_SAVE

def key_sbeg():
    """
    Shifted Beg (beginning)
    """
    return _curses.KEY_SBEG

def key_scancel():
    """
    Shifted Cancel
    """
    return _curses.KEY_SCANCEL

def key_scommand():
    """
    Shifted Command
    """
    return _curses.KEY_SCOMMAND

def key_scopy():
    """
    Shifted Copy
    """
    return _curses.KEY_SCOPY

def key_screate():
    """
    Shifted Create
    """
    return _curses.KEY_SCREATE

def key_sdc():
    """
    Shifted Delete char
    """
    return _curses.KEY_SDC

def key_sdl():
    """
    Shifted Delete line
    """
    return _curses.KEY_SDL

def key_select():
    """
    Select
    """
    return _curses.KEY_SELECT

def key_send():
    """
    Shifted End
    """
    return _curses.KEY_SEND

def key_seol():
    """
    Shifted Clear line
    """
    return _curses.KEY_SEOL

def key_sexit():
    """
    Shifted Exit
    """
    return _curses.KEY_SEXIT

def key_sfind():
    """
    Shifted Find
    """
    return _curses.KEY_SFIND

def key_shelp():
    """
    Shifted Help
    """
    return _curses.KEY_SHELP

def key_shome():
    """
    Shifted Home
    """
    return _curses.KEY_SHOME

def key_sic():
    """
    Shifted Input
    """
    return _curses.KEY_SIC

def key_sleft():
    """
    Shifted Left arrow
    """
    return _curses.KEY_SLEFT

def key_smessage():
    """
    Shifted Message
    """
    return _curses.KEY_SMESSAGE

def key_smove():
    """
    Shifted Move
    """
    return _curses.KEY_SMOVE

def key_snext():
    """
    Shifted Next
    """
    return _curses.KEY_SNEXT

def key_soptions():
    """
    Shifted Options
    """
    return _curses.KEY_SOPTIONS

def key_sprevious():
    """
    Shifted Prev
    """
    return _curses.KEY_SPREVIOUS

def key_sprint():
    """
    Shifted Print
    """
    return _curses.KEY_SPRINT

def key_sredo():
    """
    Shifted Redo
    """
    return _curses.KEY_SREDO

def key_sreplace():
    """
    Shifted Replace
    """
    return _curses.KEY_SREPLACE

def key_sright():
    """
    Shifted Right arrow
    """
    return _curses.KEY_SRIGHT

def key_srsume():
    """
    Shifted Resume
    """
    return _curses.KEY_SRSUME

def key_ssave():
    """
    Shifted Save
    """
    return _curses.KEY_SSAVE

def key_ssuspend():
    """
    Shifted Suspend
    """
    return _curses.KEY_SSUSPEND

def key_sundo():
    """
    Shifted Undo
    """
    return _curses.KEY_SUNDO

def key_suspend():
    """
    Suspend
    """
    return _curses.KEY_SUSPEND

def key_undo():
    """
    Undo
    """
    return _curses.KEY_UNDO

def key_mouse():
    """
    Mouse event has occurred
    """
    return _curses.KEY_MOUSE

def key_resize():
    """
    Terminal resize event
    """
    return _curses.KEY_RESIZE

def key_max():
    """
    Maximum key value
    """
    return _curses.KEY_MAX

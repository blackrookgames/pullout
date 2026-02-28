all = ['BCCursesAttrFunc']

from typing import\
    Callable as _Callable

type BCCursesAttrFunc = _Callable[[int], int]
"""
Function for computing a curses character attribute

:param 0:
    boacon character attribute
:return:
    curses character attribute
"""
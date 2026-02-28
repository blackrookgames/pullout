all = ['BCSetChrFunc']

from typing import\
    Callable as _Callable

from .c_BCChar import\
    BCChar as _BCChar

type BCSetChrFunc = _Callable[[int, int, _BCChar], None]
"""
Function for a placing a character

:param 0:
    X-coordinate
:param 1:
    Y-coordinate
:param 2:
    boacon character
"""
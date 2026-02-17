all = ['BCState']

from enum import\
    auto as _auto,\
    Enum as _Enum

class BCState(_Enum):
    """
    Represents the state of the boacon system
    """
    NORUN = _auto()
    INIT = _auto()
    RUN = _auto()
    FINAL = _auto()
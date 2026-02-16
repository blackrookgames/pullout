all = ['CLIErrorType']

from enum import\
    auto as _auto,\
    Enum as _Enum

class CLIErrorType(_Enum):
    """
    Represents a type of CLI-related error
    """

    MISC = _auto()
    """Misc error"""

    DDOS = _auto()
    """Error caused by DDOS protection"""

    NETWORK = _auto
    """Network error"""


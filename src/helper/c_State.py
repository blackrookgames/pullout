all = ['State']

from enum import\
    auto as _auto,\
    Enum as _Enum

from .c_BadOpError import\
    BadOpError as _BadOpError

class State(_Enum):
    """
    Represents the current state of something
    """
    
    #region constants

    NOTRUN = _auto()
    INIT = _auto()
    RUN = _auto()
    FINAL = _auto()

    #endregion

    #region methods
    
    def raise_if_notrunning(self, obj:object):
        """
        Raises a BadOpError if the value != RUN

        :param obj:
            Related object
        :raise BadOpError:
            self != RUN
        """
        if self == self.RUN: return
        raise _BadOpError(f"{obj} is not currently running.")

    #endregion
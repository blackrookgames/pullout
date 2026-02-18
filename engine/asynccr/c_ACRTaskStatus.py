all = ['ACRTaskStatus']

from enum import\
    auto as _auto,\
    Enum as _Enum

class ACRTaskStatus(_Enum):
    """
    Represents the status of an async task
    """

    INIT = _auto()
    """Task has been initialized, but has not yet been executed"""

    RUN = _auto()
    """Task is currently executing"""

    SUCCESS = _auto()
    """Task has completed successfully"""

    ERROR = _auto()
    """An error occurred while executing the task"""
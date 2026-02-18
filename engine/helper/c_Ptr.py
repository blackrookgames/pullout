all = ['Ptr']

from typing import\
    Generic as _Generic,\
    TypeVar as _TypeVar

T = _TypeVar("T")

class Ptr(_Generic[T]):
    """
    Represents a "pointer" to a value
    """

    #region init

    def __init__(self):
        """
        Initializer for Ptr
        """
        self.__value:None|T = None

    #endregion

    #region properties

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, v:T):
        self.__value = v

    #endregion
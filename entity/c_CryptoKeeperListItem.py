all = ['CryptoKeeperListItem']

from typing import\
    Generic as _Generic,\
    TypeVar as _TypeVar

T = _TypeVar('T')

class CryptoKeeperListItem(_Generic[T]):
    """
    Represents an item in a list used by a crypto keeper
    """

    #region init

    def __init__(self, name:str, value:T):
        """
        Initializer for CryptoKeeperListItem

        :param name:
            Item name
        :param value:
            Item value
        """
        self.__name = name
        self.__value = value

    #endregion

    #region properties

    @property
    def name(self):
        """
        Item name
        """
        return self.__name

    @property
    def value(self):
        """
        Item value
        """
        return self.__value

    #endregion

    #region helper methods

    def _set_value(self, value:T):
        """
        Also accessed by CryptoKeeperListAccess
        """
        self.__value = value

    #endregion
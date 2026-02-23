all = ['CryptoKeeperList']

from typing import\
    Generic as _Generic,\
    TypeVar as _TypeVar

from .c_CryptoKeeperListAccess import\
    CryptoKeeperListAccess as _CryptoKeeperListAccess

T = _TypeVar('T')

class CryptoKeeperList(_Generic[T]):
    """
    Represents a list used by a crypto keeper
    """

    #region init

    def __init__(self, items:_CryptoKeeperListAccess[T]):
        """
        Initializer for CryptoKeeperList
        """
        self.__items = items

    #endregion

    #region operators

    def __len__(self):
        return len(self.__items)

    def __iter__(self):
        for _item in self.__items:
            yield _item

    def __getitem__(self, indexorname:int|str):
        return self.__items[indexorname]

    def __contains__(self, name:str):
        return name in self.__items
    
    #endregion
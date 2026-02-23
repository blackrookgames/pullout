all = ['CryptoKeeperListAccess']

from typing import\
    Generic as _Generic,\
    TypeVar as _TypeVar

from .c_CryptoKeeperListItem import\
    CryptoKeeperListItem as _CryptoKeeperListItem

T = _TypeVar('T')

class CryptoKeeperListAccess(_Generic[T]):
    """
    Represents modifiable access to a list used by a crypto keeper
    """

    #region init

    def __init__(self):
        """
        Initializer for CryptoKeeperListAccess
        """
        self.__indexes:dict[str, int] = {}
        self.__items:list[_CryptoKeeperListItem[T]] = []

    #endregion

    #region operators

    def __len__(self):
        return len(self.__items)

    def __iter__(self):
        for _item in self.__items:
            yield _item

    def __getitem__(self, indexorname:int|str):
        return self.__items[self.__index(indexorname)]

    def __setitem__(self, indexorname:int|str, value:T):
        item = self.__items[self.__index(indexorname)]
        item._set_value(value)
    
    def __contains__(self, name:str):
        return name in self.__indexes

    #endregion

    #region helper methods

    def __index(self, indexorname:int|str):
        if isinstance(indexorname, int):
            if indexorname < 0 or indexorname >= len(self.__items):
                raise IndexError("Index is out of range.")
            return indexorname
        else:
            try:
                return self.__indexes[indexorname]
            except KeyError:
                e = KeyError("Could not find an item with the specified name")
            raise e
    
    def __update_indexes(self, start:int):
        for _i in range(start, len(self.__items)):
            self.__indexes[self.__items[_i].name] = _i

    #endregion

    #region methods

    def add(self, name:str, value:T):
        """
        Adds an item to the list

        :param name:
            Item name
        :param value:
            Item value
        :raises KeyError:
            Name already exists within list
        """
        if name in self.__indexes:
            raise KeyError("Name already exists within list.")
        item = _CryptoKeeperListItem(name, value)
        self.__indexes[name] = len(self.__items)
        self.__items.append(item)
    
    def insert(self, index:int, name:str, value:T):
        """
        Inserts an item into the list

        :param index:
            Index
        :param name:
            Item name
        :param value:
            Item value
        :raises IndexError:
            Index is out of range
        :raises KeyError:
            Name already exists within list
        """
        if index < 0 or index > len(self.__items):
            raise IndexError("Index is out of range.")
        if name in self.__indexes:
            raise KeyError("Name already exists within list.")
        item = _CryptoKeeperListItem(name, value)
        self.__indexes[name] = index
        self.__items.insert(index, item)
        self.__update_indexes(index + 1)
    
    def remove(self, name:str):
        """
        Attempts to remove the item with the specified name from the list

        :param name:
            Name of item to remove
        :return:
            True if the item was found and removed; otherwise false
        """
        if not (name in self.__indexes): return False
        index = self.__indexes[name]
        self.__indexes.pop(name)
        self.__items.pop(index)
        self.__update_indexes(index)
        return True

    def removeat(self, index:int):
        """
        Removes the item at the specified index from the list

        :param index:
            Index of item to remove
        :raises IndexError:
            Index is out of range
        """
        if index < 0 or index >= len(self.__items):
            raise IndexError("Index is out of range.")
        self.__indexes.pop(self.__items[index].name)
        self.__items.pop(index)
        self.__update_indexes(index)

    def clear(self):
        """
        Removes all items from the list
        """
        self.__indexes.clear()
        self.__items.clear()

    #endregion
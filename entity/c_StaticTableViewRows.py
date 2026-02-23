all = ['StaticTableViewRows']

from collections.abc import\
    Iterable as _Iterable
from typing import\
    TYPE_CHECKING as _TYPE_CHECKING

import engine.app as _app
import engine.boacon as _boacon

if _TYPE_CHECKING:
    from .c_StaticTableView import StaticTableView as _StaticTableView

_SPACE = _boacon.BCChar(0x20)

class StaticTableViewRows:
    """
    Represents the rows within a "static" table view
    """

    #region init

    def __init__(self,\
            view:'_StaticTableView',\
            columnwidths:_Iterable[int],\
            rows:None|_Iterable[_Iterable[None|_boacon.BCStr|str|object]]):
        """
        Initializer for StaticTableViewRows

        :param view:
            Table view
        """
        # View
        self.__view = view
        # Columns
        self.__columnwidths = tuple([max(0, _width) for _width in columnwidths])
        # Rows
        self.__rows:list[tuple[_boacon.BCStr]] = []
        if rows is not None:
            for _row in rows:
                self.__rows.append(self.__newrow(_row))

    #endregion

    #region operators

    def __len__(self):
        return len(self.__rows)
    
    def __iter__(self):
        for _row in self.__rows:
            yield _row
    
    def __getitem__(self, index:int):
        if index < 0 or index >= len(self.__rows):
            raise IndexError("Index is out of range")
        return self.__rows[index]
    
    def __setitem__(self, index:int, row:_Iterable[None|_boacon.BCStr|str|object]):
        if index < 0 or index >= len(self.__rows):
            raise IndexError("Index is out of range")
        self.__rows[index] = self.__newrow(row)
        self.__view._view_update()

    #endregion

    #region properties

    @property
    def columnwidths(self):
        """
        Widths of each column
        """
        return self.__columnwidths

    #endregion

    #region helper methods

    def __newrow(self, row:_Iterable[None|_boacon.BCStr|str|object]):
        _newrow:list[_boacon.BCStr] = []
        _index = 0
        for _column in row:
            if _index >= len(self.__columnwidths):
                break
            # Add column
            if isinstance(_column, _boacon.BCStr):
                _newrow.append(_column)
            else:
                _newrow.append(_boacon.BCStr(_column))
            # Next
            _index += 1
        return tuple[_boacon.BCStr](_newrow)

    #endregion

    #region methods

    def add(self, row:_Iterable[None|_boacon.BCStr|str|object]):
        """
        Adds a new row to the table

        :param row:
            Row data
        """
        self.__rows.append(self.__newrow(row))
        self.__view._view_update()

    def insert(self, index:int, row:_Iterable[None|_boacon.BCStr|str|object]):
        """
        Inserts a new row into the table

        :param index:
            Index to insert new row
        :param row:
            Row data
        :raise IndexError:
            Index is out of range
        """
        if index < 0 or index > len(self.__rows):
            raise IndexError("Index is out of range.")
        self.__rows.insert(index, self.__newrow(row))
        self.__view._view_update()

    def removeat(self, index:int):
        """
        Removes the row at the specified index from the table

        :param index:
            Index of row to remove
        :raise IndexError:
            Index is out of range
        """
        if index < 0 or index >= len(self.__rows):
            raise IndexError("Index is out of range.")
        self.__rows.pop(index)
        self.__view._view_update()
    
    def clear(self):
        """
        Removes all rows from the table
        """
        self.__rows.clear()
        self.__view._view_update()

    #endregion
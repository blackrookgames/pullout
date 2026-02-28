all = ['StaticTableView']

import curses as _curses

from collections.abc import\
    Iterable as _Iterable

import engine.app as _app
import engine.boacon as _boacon

from .c_StaticTableViewRows import\
    StaticTableViewRows as _StaticTableViewRows

_SPACE = _boacon.BCChar(0x20)

class StaticTableView(_app.AppPaneObject):
    """
    Represents a "static" display of a table
    """

    #region init

    def __init__(self,\
            columnwidths:_Iterable[int],\
            rows:None|_Iterable[_Iterable[None|_boacon.BCStr|str|object]] = None):
        """
        Initializer for StaticTableView

        :param columnwidths:
            Widths of each column
        :param rows:
            Initial rows
        """
        super().__init__()
        self.focusable = True
        # Rows
        self.__rows = _StaticTableViewRows(self, columnwidths, rows)
        # View
        self.__view_offset = 0
        # Prev
        self.__prev_width = 0
        self.__prev_height = 0

    #endregion

    #region properties

    @property
    def rows(self):
        """
        Table rows
        """
        return self.__rows

    #endregion

    #region helper methods

    def _view_update(self, dontupdatechrs:bool = False):
        """
        Also accessed by StaticTableViewRows
        """
        if self._chars.height > 0 and self._chars.height < len(self.__rows):
            if (self.__view_offset + self._chars.height) > len(self.__rows):
                self.__view_offset = len(self.__rows) - self._chars.height
            if self.__view_offset < 0:
                self.__view_offset = 0
        else:
            self.__view_offset = 0
        if not dontupdatechrs:
            self._update_chrs()

    #endregion

    #region AppObjectPane
    
    def _resolved(self):
        self.__prev_width = self._chars.width
        self.__prev_height = self._chars.height
        super()._resolved()
    
    def _refreshbuffer(self):
        super()._refreshbuffer()
        if self._chars.width != self.__prev_width or self._chars.height != self.__prev_height:
            self._view_update(dontupdatechrs = True)
        _oindex = 0
        # Draw rows
        for _i in range(min(self._chars.height, len(self.__rows))):
            _rest = self._chars.width
            # Draw row content
            _row = self.__rows[self.__view_offset + _i]
            for _j in range(len(_row)):
                # Make sure there's room
                if _rest == 0: break
                # Get cell and cell width
                _cell = _row[_j]
                _cellrest = min(_rest, self.__rows.columnwidths[_j])
                # Draw cell content
                for _k in range(min(_cellrest, len(_cell))):
                    self._chars[_oindex] = _cell[_k]
                    _oindex += 1
                    _rest -= 1
                    _cellrest -= 1
                # Fill rest of cell with spaces
                while _cellrest > 0:
                    self._chars[_oindex] = _SPACE
                    _oindex += 1
                    _rest -= 1
                    _cellrest -= 1
            # Fill rest of row with spaces
            while _rest > 0:
                self._chars[_oindex] = _SPACE
                _oindex += 1
                _rest -= 1
        # Fill rest
        while _oindex < len(self._chars):
            self._chars[_oindex] = _SPACE
            _oindex += 1

    #endregion

    #region AppObject

    def _update(self, params:_app.AppUpdate):
        super()._update(params)
        # Check keys
        if self.hasfocus:
            match params.key:
                case _curses.KEY_UP:
                    self.__view_offset -= 1
                    self._view_update()
                case _curses.KEY_DOWN:
                    self.__view_offset += 1
                    self._view_update()

    #endregion
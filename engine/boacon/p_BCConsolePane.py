all = ['BCConsolePane']

import numpy as _np

from typing import\
    Callable as _Callable,\
    cast as _cast

from .c_BCChar import\
    BCChar as _BCChar
from .c_BCPane import\
    BCPane as _BCPane
from .c_BCStr import\
    BCStr as _BCStr

class BCConsolePane(_BCPane):
    """
    Represents a pane with a console-like display
    """

    #region const

    __DEF_LINES_SIZE = 64

    __SPACE = _BCChar(0x20)

    #endregion

    #region init

    def __init__(self):
        """
        Initializer for BCConsolePane
        """
        super().__init__()
        self.__format_linebuffer(self.__DEF_LINES_SIZE)
        self.__format_charbuffer(0, 0)

    #endregion

    #region properties

    @property
    def lines_size(self):
        """
        Size of line buffer
        """
        return self.__lines_size

    #endregion

    #region helper methods
    
    def _resolved(self):
        if self.__chars_w == self.x.pntlen and self.__chars_h == self.y.pntlen:
            return
        self.__format_charbuffer(self.x.pntlen, self.y.pntlen)
        self.__update_charbuffer()
    
    def _draw(self, setchr:_Callable[[int, int, _BCChar], None]):
        # Make sure pane has a valid size
        if self.__chars_w == 0 or self.__chars_h == 0:
            return
        # Copy to screen
        iy = self.y.clipoff
        oy = self.y.clip0
        while oy < self.y.clip1:
            ix = self.x.clipoff
            ox = self.x.clip0
            while ox < self.x.clip1:
                setchr(ox, oy, self.__chars[iy * self.__chars_w + ix])
                ix += 1
                ox += 1
            iy += 1
            oy += 1
    
    def __format_linebuffer(self, size:int):
        """
        Assume
        - size >= 0
        """
        self.__lines_size = size
        self.__lines_feed = 0
        self.__lines_count = 0
        self.__lines = _np.full(self.__lines_size, None, dtype = object)

    def __format_charbuffer(self, width:int, height:int):
        """
        Assume
        - width >= 0
        - height >= 0
        """
        self.__chars_w = width
        self.__chars_h = height
        self.__chars = _np.full(self.__chars_w * self.__chars_h, self.__SPACE, dtype = object)
    
    def __update_charbuffer(self):
        # Make sure pane has a valid size
        if self.__chars_w == 0 or self.__chars_h == 0:
            return
        # Add text to buffer
        _out_index = len(self.__chars)
        _line_cnt = 0
        _line_off = self.__lines_feed - 1
        while _out_index > 0 and _line_cnt < self.__lines_count:
            _line = self.__lines[_line_off]
            # Print spaces
            _line_space = self.__chars_w - (len(_line) % self.__chars_w)
            if len(_line) > 0 and _line_space == self.__chars_w:
                _line_space = 0
            while _line_space > 0:
                _out_index -= 1
                _line_space -= 1
                self.__chars[_out_index] = self.__SPACE
            # Print text
            _line_index = len(_line)
            while _out_index > 0 and _line_index > 0:
                _out_index -= 1
                _line_index -= 1
                self.__chars[_out_index] = _line[_line_index]
            # Next line
            _line_cnt += 1
            _line_off = (_line_off + self.__lines_size - 1) % self.__lines_size
        # Mark dirty
        self.set_dirty()

    #endregion

    #region methods

    def format(self, lines_size:int = __DEF_LINES_SIZE):
        """
        Formats the console.\n
        NOTE: All existing data will be erased.

        :param lines_size:
            Size of line buffer.
        :raise ValueError:
            lines_size is less than zero.
        """
        if lines_size < 0:
            raise ValueError("lines_size must be greater than or equal to zero.")
        self.__format_linebuffer(lines_size)

    def print(self, text:None|_BCStr|str|object = None):
        """
        Prints text to the console

        :param text:
            Text to print
        """
        def _addline(_text:_BCStr):
            if self.__lines_size == 0: return
            # Add line
            self.__lines[self.__lines_feed] = _text
            # Update count
            if self.__lines_count < self.__lines_size:
                self.__lines_count += 1
            # Update feed
            self.__lines_feed = (self.__lines_feed + 1) % self.__lines_size
        # Normalize text 
        if not isinstance(text, _BCStr):
            text = _BCStr(text)
        # Split text into lines
        _beg = 0
        for _i in range(len(text)):
            if text[_i].ord != 0x0A:
                continue
            _addline(text.substr(beg = _beg, end = _i))
            _beg = _i + 1
        _addline(text.substr(beg = _beg))
        # Update character buffer
        self.__update_charbuffer()

    #endregion
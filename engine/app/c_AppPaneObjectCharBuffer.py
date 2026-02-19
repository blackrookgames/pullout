all = ['AppPaneObjectCharBuffer']

import numpy as _np

from engine.boacon import\
    BCChar as _BCChar

_SPACE = _BCChar(0x20)

class AppPaneObjectCharBuffer:
    """
    Represents a character buffer for a pane object
    """

    #region init

    def __init__(self):
        """
        Initializer for AppPaneObjectCharBuffer
        """
        self.__width = 0
        self.__height = 0
        self.__chars = _np.full(0, _SPACE, dtype = object)

    #endregion

    #region operators

    def __len__(self):
        return len(self.__chars)
    
    def __getitem__(self, index:int) -> _BCChar:
        try:
            return self.__chars[index]
        except Exception as _e:
            if index < 0 or index >= len(self.__chars):
                e = IndexError("Index is out of range.")
            else: e = _e
        raise e
    
    def __setitem__(self, index:int, char:_BCChar):
        try:
            self.__chars[index] = char
            return
        except Exception as _e:
            if index < 0 or index >= len(self.__chars):
                e = IndexError("Index is out of range.")
            else: e = _e
        raise e

    #endregion

    #region properties

    @property
    def width(self):
        """
        Width of buffer
        """
        return self.__width

    @property
    def height(self):
        """
        Height of buffer
        """
        return self.__height

    #endregion

    #region helper methods

    def _format(self, width:int, height:int):
        """
        Assume
        - width >= 0
        - height >= 0
        \n
        Also accessed by AppPaneObject
        """
        self.__width = width
        self.__height = height
        self.__chars = _np.full(\
            self.__width * self.__height,\
            _SPACE, dtype = object)

    #endregion
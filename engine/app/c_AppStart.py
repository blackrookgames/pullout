all = ['AppStart']

from typing import\
    Any as _Any

from .c_AppObject import\
    AppObject as _AppObject

class AppStart:
    """
    Represents parameters for executing the main application code
    """

    #region init

    def __init__(self):
        """
        Initializer for AppStart
        """
        self.__apipath = ""
        self.__objects:list[_AppObject] = []
        self.__con_left:None|int = 1
        self.__con_right:None|int = 1
        self.__con_width:None|int = None
        self.__con_top:None|int = 1
        self.__con_bottom:None|int = 1
        self.__con_height:None|int = None

    #endregion

    #region properties

    @property
    def apipath(self):
        """
        Path of API JSON file
        """
        return self.__apipath
    @apipath.setter
    def apipath(self, value:_Any):
        self.__apipath = value

    @property
    def con_left(self):
        """
        Offset from left edge of terminal to left edge of console pane
        """
        return self.__con_left
    @con_left.setter
    def con_left(self, value:_Any):
        self.__con_left = value

    @property
    def con_right(self):
        """
        Offset from right edge of terminal to right edge of console pane
        """
        return self.__con_right
    @con_right.setter
    def con_right(self, value:_Any):
        self.__con_right = value

    @property
    def con_width(self):
        """
        Width of console pane
        """
        return self.__con_width
    @con_width.setter
    def con_width(self, value:_Any):
        self.__con_width = value

    @property
    def con_top(self):
        """
        Offset from top edge of terminal to top edge of console pane
        """
        return self.__con_top
    @con_top.setter
    def con_top(self, value:_Any):
        self.__con_top = value

    @property
    def con_bottom(self):
        """
        Offset from bottom edge of terminal to bottom edge of console pane
        """
        return self.__con_bottom
    @con_bottom.setter
    def con_bottom(self, value:_Any):
        self.__con_bottom = value

    @property
    def con_height(self):
        """
        Height of console pane
        """
        return self.__con_height
    @con_height.setter
    def con_height(self, value:_Any):
        self.__con_height = value

    @property
    def objects(self):
        """
        Objects to add to the update pool
        """
        return self.__objects

    #endregion
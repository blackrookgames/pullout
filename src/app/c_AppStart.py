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
    def objects(self):
        """
        Objects to add to the update pool
        """
        return self.__objects

    #endregion
all = ['BCPostDrawArgs']

import curses as _curses

from .c_BCCursesAttrFunc import\
    BCCursesAttrFunc as _BCCursesAttrFunc
from .c_BCSetChrFunc import\
    BCSetChrFunc as _BCSetChrFunc

class BCPostDrawArgs:
    """
    Represents post-draw arguments
    """

    #region init

    def __init__(self,\
            win:_curses.window,\
            cursesattr:_BCCursesAttrFunc,\
            setchr:_BCSetChrFunc):
        self.__win = win
        self.__cursesattr = cursesattr
        self.__setchr = setchr

    #endregion

    #region properties
    
    @property
    def win(self):
        """
        Curses window
        """
        return self.__win
    
    @property
    def cursesattr(self):
        """
        Function for computing a curses character attribute
        """
        return self.__cursesattr
    
    @property
    def setchr(self):
        """
        Function for placing a character on the screen
        """
        return self.__setchr

    #endregion
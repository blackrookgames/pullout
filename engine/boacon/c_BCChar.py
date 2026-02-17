all = ['BCChar']

from .g_attr import\
    ATTR_NORMAL as _ATTR_NORMAL

class BCChar:
    """
    Represents a text character
    """

    #region init

    def __init__(self, ord:int, attr:int = _ATTR_NORMAL):
        """
        Initializer for BBChar
        
        :param ord:
            Ordinal code
        :param attr:
            Text attribute
        """
        self.__ord = ord
        self.__attr = attr

    #endregion

    #region operators

    def __repr__(self):
        return f"BCChar({self.__ord}, attr = {self.__attr})"
    
    def __str__(self):
        return chr(self.__ord)
    
    def __eq__(self, other:object):
        equ = self.__equ(other)
        if equ is None: return NotImplemented
        return equ
    
    def __ne__(self, other:object):
        equ = self.__equ(other)
        if equ is None: return NotImplemented
        return not equ
    
    def __lt__(self, other:object):
        cmp = self.__cmp(other)
        if cmp is None: return NotImplemented
        return cmp < 0
    
    def __le__(self, other:object):
        cmp = self.__cmp(other)
        if cmp is None: return NotImplemented
        return cmp <= 0
    
    def __gt__(self, other:object):
        cmp = self.__cmp(other)
        if cmp is None: return NotImplemented
        return cmp > 0
    
    def __ge__(self, other:object):
        cmp = self.__cmp(other)
        if cmp is None: return NotImplemented
        return cmp >= 0
    
    def __hash__(self):
        return self.__ord

    #endregion

    #region properties

    @property
    def ord(self):
        """
        Ordinal code
        """
        return self.__ord
    
    @property
    def attr(self):
        """
        Text attribute
        """
        return self.__attr

    #endregion

    #region helper methods

    def __equ(self, other: object):
        if isinstance(other, BCChar):
            return self.__ord == other.__ord and self.__attr == other.__attr
        if isinstance(other, str):
            return len(other) == 1 and self.__ord == ord(other)
        return None

    def __cmp(self, other: object) -> None|int:
        if isinstance(other, BCChar):
            if self.__ord != other.__ord: return self.__ord - other.__ord
            return self.__attr - other.__attr
        if isinstance(other, str):
            if len(other) != 1: return None
            return self.__ord - ord(other)
        return None
    
    #endregion

    #region methods

    def equ(self, other:object):
        """
        Checks if the character is equal to another character
        
        :param other:
            Other character
        :return:
            Whether or not the two characters are equal
        """
        equ = self.__equ(other)
        if equ is None: return False
        return equ
    
    def cmp(self, other:object):
        """
        Compares the character to another character
        
        :param other:
            Other character
        :return:
            lt 0: Current character precedes other character\n
            eq 0: Current character is equal to the other character\n
            gt 0: Current character follows other character
        :raise TypeError:
            Cannot compare with other type
        """
        cmp = self.__cmp(other)
        if cmp is None: raise TypeError(f"Cannot compare BCChar with {type(other)}.")
        return cmp

    #endregion
all = ['BCStr']

import numpy as _np

from io import\
    StringIO as _StringIO
from typing import\
    cast as _cast
from collections.abc import\
    Iterable as _Iterable

from .c_BCChar import\
    BCChar as _BCChar
from .g_attr import\
    ATTR_NORMAL as _ATTR_NORMAL

class BCStr:
    """
    Represents a string of text characters
    """

    #region nested

    class __Substr:
        def __init__(self, src, beg:int, end:int):
            """
            Assume:
            - src is BCStr
            - beg and end are in a valid range
            """
            self.src = _cast(BCStr, src)
            self.beg = beg
            self.end = end

    #endregion

    #region init

    def __init__(self, src:None|str|object|_Iterable, attr:None|int = None):
        """
        Initializer for BCStr
        
        :param src:
            Source
        :param attr:
            Character attributes
        """
        # None?
        if src is None:
            self.__data = _np.empty(0, dtype = object)
        # Substr?
        elif isinstance(src, self.__Substr):
            self.__data = self.__fromdata(src.src, src.beg, src.end, attr)
        # BCStr?
        elif isinstance(src, BCStr):
            self.__data = self.__fromdata(src, 0, len(src.__data), attr)
        # BCChar?
        elif isinstance(src, _BCChar):
            self.__data = _np.empty(1, dtype = object)
            self.__data[0] = src if (attr is None) else _BCChar(src.ord, attr = attr)
        # String?
        elif isinstance(src, str):
            self.__data = self.__fromstr(src, attr)
        # Iterable?
        elif isinstance(src, _Iterable):
            _src:list[_BCChar] = []
            self.__additer(_src, src, attr)
            self.__data = _np.empty(len(_src), dtype = object)
            for _i in range(len(_src)):
                self.__data[_i] = _src[_i]
        # Anything else?
        else:
            self.__data = self.__fromstr(str(src), attr)

    #endregion

    #region operators
    
    def __str__(self):
        with _StringIO() as strio:
            for char in self.__data:
                strio.write(str(char))
            return strio.getvalue()

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
        return len(self.__data)

    def __len__(self):
        return len(self.__data)
    
    def __getitem__(self, index:object):
        if not isinstance(index, int):
            raise TypeError(f"Cannot use {type(index)} as an index value.")
        if index < 0 or index >= len(self.__data):
            raise IndexError("Index is out of range.")
        return _cast(_BCChar, self.__data[index])
    
    def __iter__(self):
        for item in self.__data:
            yield _cast(_BCChar, item)

    #endregion
    
    #region helper methods

    @classmethod
    def ___equ(cls, array0, array1):
        if len(array0) != len(array1):
            return False
        for i in range(len(array0)):
            if array0[i] != array1[i]:
                return False
        return True

    @classmethod
    def ___cmp(cls, array0, array1):
        # Compare lengths
        lencmp = len(array0) - len(array1)
        minlen = len(array1) if (lencmp > 0) else len(array0)
        # Compare characters
        for i in range(len(array0)):
            chrcmp = _cast(_BCChar, array0[i]).cmp(array1[i])
            if chrcmp != 0: return chrcmp
        # Return length comparison
        return lencmp

    def __equ(self, other:object):
        if isinstance(other, BCStr):
            return self.___equ(self.__data, other.__data)
        if isinstance(other, str):
            return self.___equ(self.__data, other)
        if isinstance(other, _BCChar):
            if len(self.__data) != 1:
                return False
            return _cast(_BCChar, self.__data[0]).equ(other)
        return None
    
    def __cmp(self, other:object):
        if isinstance(other, BCStr):
            return self.___cmp(self.__data, other.__data)
        if isinstance(other, str):
            return self.___cmp(self.__data, other)
        if isinstance(other, _BCChar):
            if len(self.__data) != 1:
                return len(self.__data) - 1
            return _cast(_BCChar, self.__data[0]).cmp(other)
        return None

    @classmethod
    def __fromdata(cls, src, beg:int, end:int, attr:None|int):
        assert isinstance(src, BCStr)
        data = _np.empty(end - beg, dtype = object)
        if attr is None:
            for _i in range(len(data)):
                _chr = _cast(_BCChar, src.__data[beg + _i])
                data[_i] = _chr
        else:
            for _i in range(len(data)):
                _chr = _cast(_BCChar, src.__data[beg + _i])
                data[_i] = _BCChar(_chr.ord, attr = attr)
        return data

    @classmethod
    def __fromstr(cls, src:str, attr:None|int):
        if attr is None: attr = _ATTR_NORMAL
        data = _np.empty(len(src), dtype = object)
        for _i in range(len(src)):
            data[_i] = _BCChar(ord(src[_i]), attr = attr)
        return data

    @classmethod
    def __adddata(cls, chars:list[_BCChar], src, attr:None|int):
        assert isinstance(src, BCStr)
        if attr is None:
            for _i in range(len(src.__data)):
                _chr = _cast(_BCChar, src.__data[_i])
                chars.append(_chr)
        else:
            for _i in range(len(src.__data)):
                _chr = _cast(_BCChar, src.__data[_i])
                chars.append(_BCChar(_chr.ord, attr = attr))
    
    @classmethod
    def __addstr(cls, chars:list[_BCChar], src:str, attr:None|int):
        if attr is None: attr = _ATTR_NORMAL
        for _i in range(len(src)):
            chars.append(_BCChar(ord(src[_i]), attr = attr))

    @classmethod
    def __additer(cls, chars:list[_BCChar], src:_Iterable, attr:None|int):
        for _item in src:
            # None?
            if _item is None: continue
            # BCStr?
            elif isinstance(_item, BCStr):
                cls.__adddata(chars, _item, attr)
            # BCChar?
            elif isinstance(_item, _BCChar):
                chars.append(_item if (attr is None) else _BCChar(_item.ord, attr = attr))
            # String?
            elif isinstance(_item, str):
                cls.__addstr(chars, _item, attr)
            # Iterable?
            elif isinstance(_item, _Iterable):
                cls.__additer(chars, _item, attr = attr)
            # Anything else?
            else:
                cls.__addstr(chars, str(_item), attr)

    #endregion

    #region methods

    def equ(self, other:object):
        """
        Checks if the string is equal to another string
        
        :param other:
            Other string
        :return:
            Whether or not the two strings are equal
        """
        equ = self.__equ(other)
        if equ is None: return False
        return equ
    
    def cmp(self, other:object):
        """
        Compares the string to another string
        
        :param other:
            Other string
        :return:
            lt 0: Current string precedes other string\n
            eq 0: Current string is equal to the other string\n
            gt 0: Current string follows other string
        :raise TypeError:
            Cannot compare with other type
        """
        cmp = self.__cmp(other)
        if cmp is None: raise TypeError(f"Cannot compare BCStr with {type(other)}.")
        return cmp

    def substr(self, beg:None|int = None, end:None|int = None):
        """
        Creates a substring
        
        :param beg:
            Beginning index (if negative, index is relative to end of string)
        :param end:
            End index (if negative, index is relative to end of string)
        :return:
            Created substring
        :raise IndexError:
            Beginning index is out of range\n
            or\n
            End index is out of range\n
            or\n
            End index precedes beginning index
        """
        # Beginning
        if beg is not None:
            if beg < 0: beg += len(self.__data)
            if beg < 0 or beg > len(self.__data):
                raise IndexError("Beginning index is out of range.") 
        else: beg = 0
        # End
        if end is not None:
            if end < 0: end += len(self.__data)
            if end < 0 or end > len(self.__data):
                raise IndexError("End index is out of range.")
        else: end = len(self.__data)
        # Make sure indexes are valid
        if end < beg: raise IndexError("End index cannot precede beginning index.")
        return BCStr(self.__Substr(self, beg, end))

    #endregion
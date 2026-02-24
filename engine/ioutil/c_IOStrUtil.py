all = ['IOStrUtil']

from io import\
    BufferedReader as _BufferedReader,\
    BufferedWriter as _BufferedWriter

from ..helper.c_CLIError import\
    CLIError as _CLIError
from ..helper.c_const import\
    U64_MAX as _U64_MAX

class IOStrUtil:
    """
    Utility for IO operations related to strings 
    """

    @classmethod
    def safestr_read(cls, reader:_BufferedReader):
        """
        Reads a "safe" string from a file

        :param reader:
            Reader
        :return:
            Read string (or None if reader is at end)
        :raise CLIError:
            An error occurred
        """
        try:
            _bytes:None|bytes = None
            def _read(_count:int):
                nonlocal reader, _bytes
                _bytes = reader.read(_count)
                if _bytes is None: return False
                if len(_bytes) < _count: return False
                return True
            #region header
            if not _read(1): return None
            assert _bytes is not None
            _byte = _bytes[0]
            # Check if string is not null-terminated
            notnull = (_byte & 0b00000001) != 0
            # Check if string characters are 16-bit
            bit16 = (_byte & 0b00000010) != 0
            # Get length info (ignored if null-terminated)
            leninfo = (_byte >> 2) & 0b00000111
            #endregion
            if notnull:
                # Get length of string
                if not _read(leninfo + 1): return ""
                strlen = 0
                for _i in range(len(_bytes) - 1, -1, -1):
                    strlen <<= 8
                    strlen |= _bytes[_i]
                # Get string characters
                _chars = [0] * strlen
                _bytes = reader.read(strlen * (2 if bit16 else 1))
                if _bytes is not None:
                    if bit16:
                        _i = 0
                        for _j in range(len(_bytes) // 2):
                            _chars[_j] = _bytes[_i] | (_bytes[_i + 1] << 8)
                            _i += 2
                    else:
                        for _i in range(len(_bytes)):
                            _chars[_i] = _bytes[_i]
            else:
                # Get string characters
                _chars:list[int] = []
                if bit16:
                    while _read(2):
                        _char = _bytes[0] | (_bytes[1] << 8)
                        if _char == 0: break
                        _chars.append(_char)
                else:
                    while _read(1):
                        _char = _bytes[0]
                        if _char == 0: break
                        _chars.append(_char)
            return ''.join(map(chr, _chars))
        except Exception as _e: e = _CLIError(_e)
        raise e
    
    @classmethod
    def safestr_write(cls, s:str, writer:_BufferedWriter,\
            nonull:bool = False, force16:bool = False):
        """
        Writes a "safe" string to a file

        :param s:
            String to write
        :param writer:
            Writer
        :param nonull:
            Do not allow string to be written as null-terminated
        :param force16:
            Force string to be written with 16-bit characters
        :raise CLIError:
            An error occurred
        """
        try:
            # Evaluate string
            notnull = nonull
            bit16 = force16
            for _char in s:
                _ord = ord(_char)
                if _ord == 0: notnull = True
                if _ord > 0xFF: bit16 = True
            # Create data
            #region 
            length = len(s)
            # Compute length info (if non null-terminating) (truncate if too long)
            leninfo = 0
            if notnull:
                if length < _U64_MAX:
                    _max = 0xFF
                    while length > _max:
                        leninfo += 1
                        _max = (_max << 8) | 0xFF
                else:
                    length = _U64_MAX
                    leninfo = 7
            # Create array 
            _bpc = 2 if bit16 else 1
            _size = 1 + length * _bpc
            if notnull: _size += leninfo + 1 # Length value
            else: _size += _bpc # Null-terminating character
            data = bytearray(_size)
            _oindex = 0
            # Add header info
            data[_oindex] = \
                (0b00000001 if notnull else 0) | \
                (0b00000010 if bit16 else 0) | \
                (leninfo << 2)
            _oindex += 1
            # Add string length (if not null-terminating)
            if notnull:
                _value = length
                for _i in range(-1, leninfo):
                    data[_oindex] = 0xFF & _value
                    _oindex += 1
                    _value >>= 8
            # Add characters
            if bit16:
                for _i in range(length):
                    _ord = ord(s[_i])
                    data[_oindex] = 0xFF & _ord
                    data[_oindex + 1] = 0xFF & (_ord >> 8)
                    _oindex += 2
            else:
                for _i in range(length):
                    data[_oindex] = ord(s[_i])
                    _oindex += 1
            # Add null character (if null-terminating)
            if not notnull:
                data[_oindex] = 0x00
                _oindex += 1
                if bit16:
                    data[_oindex] = 0x00
                    _oindex += 1
            #endregion
            # Write data
            writer.write(data)
            # Success!!!
            return
        except _CLIError as _e: e = _e
        except Exception as _e: e = _CLIError(_e)
        raise e

    @classmethod
    def safestrs_from_file(cls, path):
        """
        Reads a list of "safe" strings from a file

        :param path:
            Path of file
        :return:
            Created list of strings
        :raise CLIError:
            An error occurred
        """
        try:
            strings:list[str] = []
            with open(path, 'rb') as f:
                while True:
                    _str = cls.safestr_read(f)
                    if _str is None: break
                    strings.append(_str)
            return strings
        except _CLIError as _e: e = _e
        except Exception as _e: e = _CLIError(_e)
        raise e

    @classmethod
    def safestrs_to_file(cls, strings:list[str], path,\
            nonull:bool = False, force16:bool = False):
        """
        Writes a list of "safe" strings to a file

        :param strings:
            List of strings to write
        :param path:
            Path of file
        :param nonull:
            Do not allow strings to be written as null-terminated
        :param force16:
            Force strings to be written with 16-bit characters
        :raise CLIError:
            An error occurred
        """
        try:
            with open(path, 'wb') as f:
                for _str in strings:
                    cls.safestr_write(_str, f, nonull = nonull, force16 = force16)
            return strings
        except _CLIError as _e: e = _e
        except Exception as _e: e = _CLIError(_e)
        raise e

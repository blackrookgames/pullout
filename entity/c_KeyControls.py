all = ['KeyControls']

import engine.app as _app
import engine.boacon as _boacon

_SPACE = _boacon.BCChar(0x20)

class KeyControls(_app.AppPaneObject):
    """
    Represents a display of the keyboard controls
    """

    #region init

    def __init__(self):
        """
        Initializer for KeyControls
        """
        super().__init__()
        # Keys/descriptions
        self.__keydescs = {\
            _boacon.BCStr(" \u2191\u2193"):\
                _boacon.BCStr("Navigate")}
        self.__quit_key = _boacon.BCStr(" Esc")
        self.__quit_desc = _boacon.BCStr("Quit program")

    #endregion

    #region AppObjectPane
    
    def _refreshbuffer(self):
        super()._refreshbuffer()
        _KEYWIDTH = 6
        _oindex = 0
        _quit_offset = len(self._chars) - self._chars.width
        def _draw(_key:_boacon.BCStr, _desc:_boacon.BCStr):
            nonlocal _oindex
            _rest = self._chars.width
            _x = 0
            # Draw key
            for _i in range(min(len(_key), min(_rest, _KEYWIDTH - 2))):
                self._chars[_oindex] = _key[_i]
                _oindex += 1
                _rest -= 1
                _x += 1
            # Draw space
            while _x < _KEYWIDTH and _rest > 0:
                self._chars[_oindex] = _SPACE
                _oindex += 1
                _rest -= 1
                _x += 1
            # Draw description
            for _i in range(min(len(_desc), _rest)):
                self._chars[_oindex] = _desc[_i]
                _oindex += 1
                _rest -= 1
                _x += 1
            # Draw space
            while _rest > 0:
                self._chars[_oindex] = _SPACE
                _oindex += 1
                _rest -= 1
                _x += 1
        # Keys/descriptions
        for _key, _desc in self.__keydescs.items():
            if _oindex < _quit_offset: _draw(_key, _desc)
        # Space
        while _oindex < _quit_offset:
            self._chars[_oindex] = _SPACE
            _oindex += 1
        # Quit key/desc
        if _oindex == _quit_offset: _draw(self.__quit_key, self.__quit_desc)

    #endregion
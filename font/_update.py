import sys

from pathlib import Path
from PIL import Image

CHAR_WIDTH = 4
CHAR_HEIGHT = 8

def main():
    if len(sys.argv) == 0: return 1
    try:
        path_cmd = Path(sys.argv[0]).parent
        path_input = path_cmd.joinpath("font.png")
        path_output = path_cmd.joinpath("__init__.py")
        # Open image
        chars:list[int] = []
        with Image.open(path_input) as image:
            _image_w, _image_h = image.size
            _chars_x = _image_w // CHAR_WIDTH
            _chars_y = _image_h // CHAR_HEIGHT
            for _char_y in range(_chars_y):
                for _char_x in range(_chars_x):
                    _off_x = _char_x * CHAR_WIDTH
                    _off_y = _char_y * CHAR_HEIGHT
                    _char = 0
                    _mask = 1
                    for _pixel_y in range(CHAR_HEIGHT):
                        for _pixel_x in range(CHAR_WIDTH):
                            _color = image.getpixel((_off_x + _pixel_x, _off_y + _pixel_y))
                            if isinstance(_color, float):
                                _value = _color >= 0.5
                            elif isinstance(_color, tuple):
                                if len(_color) == 4:
                                    _value = ((_color[0] + _color[1] + _color[2]) / 3) >= 128
                                elif len(_color) > 0:
                                    _sum = 0
                                    for _v in _color: _sum += _v
                                    _value = (_sum / len(_color)) >= 128
                                else:
                                    _value = False
                            else:
                                _value = False
                            if _value: _char |= _mask
                            _mask <<= 1
                    chars.append(_char)
        # Create init
        with open(path_output, 'w') as f:
            # Write constants
            f.write(f"CHAR_WIDTH = {CHAR_WIDTH}\n")
            f.write(f"CHAR_HEIGHT = {CHAR_HEIGHT}\n")
            # Write characters
            f.write('\n')
            f.write("_chars:list[int] = [")
            for _i in range(len(chars)):
                if (_i % 8) == 0: f.write("\\\n    ")
                f.write(f"0x{chars[_i]:08X}, ")
            f.write("]\n")
            # Write functions
            f.write('\n')
            f.write("def getchar(ord:int):\n")
            f.write("    \"\"\"\n")
            f.write("    Retrieves the pixel data of the specified character\n")
            f.write("    \n")
            f.write("    :param ord: Character ordinal\n")
            f.write("    :return: Pixel data of the specified character\n")
            f.write("    \"\"\"\n")
            f.write("    global _chars\n")
            f.write("    if ord < 0 or ord >= len(_chars): return _chars[0]\n")
            f.write("    return _chars[ord]\n")


    except Exception as _e:
        print(_e, file = sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
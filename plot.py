import math
import numpy as np
import sys

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from PIL import Image
from typing import Callable, cast, TypeVar

import cry
import engine.app as app
import engine.boacon as boacon
import engine.cli as cli
import engine.helper as helper
import engine.ioutil as ioutil
import entity
import font

TItem = TypeVar('TItem')
TValue = TypeVar('TValue')

#region helper functions

def parse_path(input:str):
    try: path = Path(input)
    except:
        print(f"\"{input}\" is not a valid path.", file = sys.stderr)
        return False, None
    return True, path

#endregion

class Cmd(cli.CLICommand):

    #region nested

    class __LogEntry:
        def __init__(self, dt:int, price:float):
            self.__dt = dt
            self.__price = price
        @property
        def dt(self): return self.__dt
        @property
        def price(self): return self.__price

    class __LogData:
        def __init__(self, crypto:str, output:Path, entries:Iterable['Cmd.__LogEntry']):
            self.__crypto = crypto
            self.__output = output
            self.__entries = tuple(sorted(entries, key = lambda _entry: _entry.dt))
            if len(self.__entries) < 2: raise helper.CLIError("Cannot create a graph with less than 2 entries.")
        @property
        def crypto(self): return self.__crypto
        @property
        def output(self): return self.__output
        @property
        def entries(self): return self.__entries

    #endregion

    #region cmd

    @property
    def _desc(self):
        return "Plot data from log files"

    __directory = cli.CLIRequiredDef(\
        name = "directory",\
        desc = "Input directory; this is where the log files are stored",\
        parse = parse_path)
    
    __crypto = cli.CLIOptionWArgDef(\
        name = "crypto",\
        short = 'c',\
        desc = "Cryptocurrency to plot",\
        default = None)
    __output = cli.CLIOptionWArgDef(\
        name = "output",\
        short = 'o',\
        desc = "If --crpyto is not defined this the prefix for output paths. " +\
            "If --crypto is defined this is the output path (*.png).",\
        default = None)
    
    __x_spaces = cli.CLIOptionWArgDef(\
        name = "x_spaces",\
        desc = "Target number of grid spaces along the X-axis; the actual number of spaces may vary.",\
        parse = cli.CLIParseUtil.to_int,\
        default = 0)
    __x_pixels = cli.CLIOptionWArgDef(\
        name = "x_pixels",\
        desc = "X-pixels per grid space",\
        parse = cli.CLIParseUtil.to_int,\
        default = 0)
    __y_spaces = cli.CLIOptionWArgDef(\
        name = "y_spaces",\
        desc = "Target number of grid spaces along the Y-axis; the actual number of spaces may vary.",\
        parse = cli.CLIParseUtil.to_int,\
        default = 0)
    __y_pixels = cli.CLIOptionWArgDef(\
        name = "y_pixels",\
        desc = "Y-pixels per grid space",\
        parse = cli.CLIParseUtil.to_int,\
        default = 0)
    
    __date = cli.CLIOptionWArgDef(\
        name = "date",\
        desc = "Date format (ex: MM/DD/YY, DD/MM/YYYY, YY/MM/DD)",\
        default = "MM/DD/YYYY")
    __time12 = cli.CLIOptionFlagDef(\
        name = "time12",\
        desc = "If specified, time is displayed in a 12-hour format")
    
    __color_bg = cli.CLIOptionWArgDef(\
        name = "color_bg",\
        desc = "Background color 0xRRGGBBAA",\
        parse = cli.CLIParseUtil.to_uint32,\
        default = 0xFFFFFFFF)
    __color_grid = cli.CLIOptionWArgDef(\
        name = "color_grid",\
        desc = "Grid color 0xRRGGBBAA",\
        parse = cli.CLIParseUtil.to_uint32,\
        default = 0x808080FF)
    __color_plot = cli.CLIOptionWArgDef(\
        name = "color_plot",\
        desc = "Plot color 0xRRGGBBAA",\
        parse = cli.CLIParseUtil.to_uint32,\
        default = 0xFF0000FF)
    __color_text = cli.CLIOptionWArgDef(\
        name = "color_text",\
        desc = "Text color 0xRRGGBBAA",\
        parse = cli.CLIParseUtil.to_uint32,\
        default = 0x000000FF)

    #endregion

    #region helper methods

    @classmethod
    def __compute_minmax(cls,\
            retrieve:Callable[[TItem], TValue],\
            iterable:Iterable[TItem])\
            -> None|tuple[TValue, TValue]:
        # Determine range
        minvalue = None
        maxvalue = None
        for _item in iterable:
            _entry = retrieve(_item)
            if minvalue is None or minvalue > _entry: # type: ignore
                minvalue = _entry
            if maxvalue is None or maxvalue < _entry: # type: ignore
                maxvalue = _entry
        if minvalue is None: return None
        return minvalue, maxvalue # type: ignore
        
    @classmethod
    def __compute_spaces(cls,\
            minvalue:TValue,\
            maxvalue:TValue,\
            ups:float):
        """
        Assume
        - minvalue <= maxvalue
        - ups > 0.0
        """
        p0 = math.floor(float(minvalue) / ups) # type: ignore
        p1 = math.ceil(float(maxvalue) / ups) # type: ignore
        return int(p1 - p0)

    @classmethod
    def __compute_ups(cls,\
            convert:Callable[[float], TValue],\
            minvalue:TValue,\
            maxvalue:TValue,\
            targetspaces:int,\
            start:float):
        """
        Assume
        - minvalue <= maxvalue
        - targetspaces > 0
        - start > 0.0
        """
        FACTORS = (1.0, 2.0, 5.0)
        ups = start
        _prev_ups = 0
        _prev_spaces = 0
        _prev_diff = 0
        while True:
            for _factor in FACTORS:
                _curr_ups = ups * _factor
                _curr_spaces = cls.__compute_spaces(minvalue, maxvalue, _curr_ups)
                _curr_diff = abs(_curr_spaces - targetspaces)
                if _curr_spaces == targetspaces:
                    return convert(_curr_ups)
                if _prev_spaces != 0:
                    if _curr_diff > _prev_diff:
                        return convert(_prev_ups)
                _prev_ups = _curr_ups
                _prev_spaces = _curr_spaces
                _prev_diff = _curr_diff
            ups *= 10.0

    @classmethod
    def __lerp(cls, p0:float, p1:float, t:float):
        if p0 == p1: return p0
        return p0 + t * (p1 - p0)
    
    @classmethod
    def __invlerp(cls, p0:float, p1:float, pt:float):
        if p0 == p1: return 0.0
        return (pt - p0) / (p1 - p0)

    @classmethod
    def __from_rgba(cls, rgba:int):
        return ((rgba >> 24) & 0xFF, (rgba >> 16) & 0xFF, (rgba >> 8) & 0xFF, rgba & 0xFF, )

    @classmethod
    def __save_image(cls, image:Image.Image, path:Path):
        try:
            image.save(path)
            return
        except Exception as _e: e = helper.CLIError(_e)
        raise e

    @classmethod
    def __getlogentries(cls, path:Path):
        try: data = ioutil.IOStrUtil.safestrs_from_file(path)
        except helper.CLIError: return
        offset = 0
        # Read number of columns
        try:
            columns = int(data[offset])
            offset += 1
        except: return
        # Get crypto names
        cryptos:list[str] = []
        try:
            for _i in range(columns):
                cryptos.append(data[offset])
                offset += 1
        except: return
        # Loop thru entries
        for _i in range((len(data) - offset) // (columns + 1)):
            # Date/time
            try:
                _rawdt = data[offset]
                _dt = helper.DTUtil.to_micro2000(datetime(\
                    int(_rawdt[:4]), int(_rawdt[4:6]), int(_rawdt[6:8]),\
                    hour = int(_rawdt[8:10]), minute = int(_rawdt[10:12]),\
                    second = int(_rawdt[12:14]), microsecond = int(_rawdt[14:20])))
                offset += 1
            except: return
            # Prices
            try:
                for _j in range(columns):
                    _price = float(data[offset])
                    yield (cryptos[_j], cls.__LogEntry(_dt, _price))
                    offset += 1
            except: return

    def __getalllogentries(self):
        def _compute_path(_prefix:str, _crypto:str):
            def _flip(_chr):
                _ord = ord(_chr)
                if (_ord >= 0x41 and _ord <= 0x5A) or (_ord >= 0x61 and _ord <= 0x7A):
                    return chr(_ord ^ 0b00100000)
                return _chr
            return Path(_prefix + ''.join(map(_flip, _crypto)) + ".png")
        try:
            self_directory = cast(Path, self.directory) # type: ignore
            self_output = cast(None|str, self.output) # type: ignore
            self_crypto = cast(None|str, self.crypto) # type: ignore
            # Get all entries
            allcryptos:dict[str, list[Cmd.__LogEntry]] = {}
            for _path in self_directory.iterdir():
                if not str(_path).endswith(".bin"):
                    continue
                for _crypto, _entry in self.__getlogentries(_path):
                    if not (_crypto in allcryptos): allcryptos[_crypto] = []
                    allcryptos[_crypto].append(_entry)
            # Create "final"
            cryptos:list[Cmd.__LogData] = []
            outpfx = self_output if (self_output is not None) else str(self_directory.joinpath("plot."))
            if self_crypto is not None:
                # Make sure crypto was found
                if not (self_crypto in allcryptos):
                    raise helper.CLIError(f"Could not find log entries for {self_crypto}.") 
                # Compute output path
                _output = Path(self_output) if (self_output is not None) else _compute_path(outpfx, self_crypto)
                # Create log data
                cryptos.append(self.__LogData(self_crypto, _output, allcryptos[self_crypto]))
            else:
                print(f"  Found {len(allcryptos)} {("entry" if (len(allcryptos) == 1) else "entries")}")
                for _crypto in allcryptos:
                    # Compute output path
                    _output = _compute_path(outpfx, _crypto)
                    # Add crypto (ignore errors)
                    try: cryptos.append(self.__LogData(_crypto, _output, allcryptos[_crypto]))
                    except: pass
            # Success!!!
            return cryptos
        except helper.CLIError as _e:
            e = _e
        except Exception as _e:
            e = helper.CLIError(_e)
        raise e
    
    def __create_plot(self, logdata:__LogData):
        self_x_spaces = cast(int, self.x_spaces) # type: ignore
        self_x_pixels = cast(int, self.x_pixels) # type: ignore
        self_y_spaces = cast(int, self.y_spaces) # type: ignore
        self_y_pixels = cast(int, self.y_pixels) # type: ignore
        self_date = cast(str, self.date) # type: ignore
        self_time12 = cast(bool, self.time12) # type: ignore
        self_color_bg = cast(int, self.color_bg) # type: ignore
        self_color_grid = cast(int, self.color_grid) # type: ignore
        self_color_plot = cast(int, self.color_plot) # type: ignore
        self_color_text = cast(int, self.color_text) # type: ignore
        # Get date/time format
        dtformat = helper.DTFormat(self_date, self_time12)
        # Compute X-spacing
        print("    Computing X-spacing")
        x_spaces = 25 if (self_x_spaces <= 0) else self_x_spaces
        x_pixels = 32 if (self_x_pixels <= 0) else self_x_pixels
        x_minmax = self.__compute_minmax(lambda _entry: _entry.dt, logdata.entries)
        assert x_minmax is not None
        x_ups = self.__compute_ups(lambda v: int(v), x_minmax[0], x_minmax[1], x_spaces, 1)
        x_spaces = self.__compute_spaces(x_minmax[0], x_minmax[1], x_ups)
        x_p0 = int(math.floor(x_minmax[0] / x_ups) * x_ups)
        x_p1 = x_p0 + x_spaces * x_ups
        # Compute Y-spacing
        print("    Computing Y-spacing")
        y_spaces = 15 if (self_y_spaces <= 0) else self_y_spaces
        y_pixels = 32 if (self_y_pixels <= 0) else self_y_pixels
        y_minmax = self.__compute_minmax(lambda _entry: _entry.price, logdata.entries)
        assert y_minmax is not None
        y_ups = self.__compute_ups(lambda v: v, y_minmax[0], y_minmax[1], y_spaces, 0.00001)
        y_spaces = self.__compute_spaces(y_minmax[0], y_minmax[1], y_ups)
        y_p0 = math.floor(y_minmax[0] / y_ups) * y_ups
        y_p1 = y_p0 + y_spaces * y_ups
        # Generating X-labels
        print("    Generating X-labels")
        x_labels:list[str] = []
        x_labels_inc = (font.CHAR_HEIGHT * 2 + x_pixels - 1) // x_pixels
        _len = 0
        for _i in range(0, x_spaces, x_labels_inc):
            _str = dtformat.create(helper.DTUtil.from_micro2000(x_p0 + x_ups * _i))
            if _len < len(_str): _len = len(_str)
            x_labels.append(_str)
        x_labels_w = _len * font.CHAR_WIDTH
        # Generating Y-labels
        print("    Generating Y-labels")
        y_labels:list[str] = []
        y_labels_inc = (font.CHAR_HEIGHT * 2 + y_pixels - 1) // y_pixels
        _len = 0
        for _i in range(0, y_spaces, y_labels_inc):
            _str = f"{round(y_p0 + y_ups * _i, 6)} {logdata.crypto}"
            if _len < len(_str): _len = len(_str)
            y_labels.append(_str)
        y_labels_w = _len * font.CHAR_WIDTH
        # Create image
        color_bg = self.__from_rgba(self_color_bg)
        color_grid = self.__from_rgba(self_color_grid)
        color_plot = self.__from_rgba(self_color_plot)
        color_text = self.__from_rgba(self_color_text)
        plot_w = x_pixels * x_spaces + 1 # Including border
        plot_h = y_pixels * y_spaces + 1 # Including border
        plot_x = 2 + y_labels_w + 2
        plot_y = 2
        image_w = plot_x + plot_w + 2
        image_h = plot_y + plot_h + 2 + x_labels_w + 2
        image = Image.new('RGBA', (image_w, image_h), color_bg)
        # Draw grid lines
        print("    Drawing grid lines")
        for _x in range(0, plot_w, x_pixels):
            for _y in range(plot_h):
                image.putpixel((plot_x + _x, plot_y + _y), color_grid)
        for _y in range(0, plot_h, y_pixels):
            for _x in range(plot_w):
                image.putpixel((plot_x + _x, plot_y + _y), color_grid)
        # Plot data
        print("    Plotting data")
        _i = 0
        _entry0 = logdata.entries[_i]
        _entry1 = logdata.entries[_i + 1]
        _prev_x = None
        _prev_y = None
        for _ox in range(plot_w):
            _ix = round(self.__lerp(x_p0, x_p1, _ox / (plot_w - 1)))
            # Compute y-input
            _iy = None
            if _ix >= _entry0.dt:
                while True:
                    if _ix >= _entry1.dt:
                        if (_i + 2) >= len(logdata.entries):
                            break
                        _i += 1
                        _entry0 = logdata.entries[_i]
                        _entry1 = logdata.entries[_i + 1]
                        continue
                    _iy = self.__lerp(_entry0.price, _entry1.price, self.__invlerp(_entry0.dt, _entry1.dt, _ix))
                    break
            if _iy is None: continue
            # Compute y-output
            _oy = round(self.__lerp(0, plot_h, self.__invlerp(y_p0, y_p1, _iy)))
            # Compute final pixel coordinates
            _curr_x = max(0, min(plot_w - 1, _ox))
            _curr_y = plot_h - 1 - max(0, min(plot_h - 1, _oy))
            if _prev_x is not None and _prev_y is not None and _prev_y != _curr_y:
                # Compute halfway
                _half = (_prev_y + _curr_y) // 2
                # Fill pixels
                _inc = 1 if (_prev_y < _curr_y) else (-1)
                _yy = _prev_y + _inc
                while _yy != _curr_y:
                    image.putpixel((plot_x + _prev_x, plot_y + _yy), color_plot)
                    _yy += _inc
            image.putpixel((plot_x + _curr_x, plot_y + _curr_y), color_plot)
            # Update previous
            _prev_x = _curr_x
            _prev_y = _curr_y
        # Draw X-labels
        print("    Drawing X-labels")
        for _i in range(len(x_labels)):
            _label = x_labels[_i]
            _offx = plot_x + x_pixels * _i * x_labels_inc
            for _char_y in range(font.CHAR_HEIGHT):
                _offy = (plot_y + plot_h + 2 + len(_label) * font.CHAR_WIDTH) - 1
                for _char in _label:
                    _pixels = font.getchar(ord(_char))
                    _mask = 1 << (_char_y * font.CHAR_WIDTH)
                    for _char_x in range(font.CHAR_WIDTH):
                        if (_pixels & _mask) != 0:
                            image.putpixel((_offx, _offy), color_text)
                        _offy -= 1
                        _mask <<= 1
                _offx += 1
        # Draw Y-labels
        print("    Drawing Y-labels")
        for _i in range(len(y_labels)):
            _label = y_labels[_i]
            _offy = (plot_y + plot_h - font.CHAR_HEIGHT) - x_pixels * _i * y_labels_inc
            for _char_y in range(font.CHAR_HEIGHT):
                _offx = plot_x - 2 - len(_label) * font.CHAR_WIDTH
                for _char in _label:
                    _pixels = font.getchar(ord(_char))
                    _mask = 1 << (_char_y * font.CHAR_WIDTH)
                    for _char_x in range(font.CHAR_WIDTH):
                        if (_pixels & _mask) != 0:
                            image.putpixel((_offx, _offy), color_text)
                        _offx += 1
                        _mask <<= 1
                _offy += 1
        # Save image
        print("    Saving image")
        self.__save_image(image, logdata.output)

    #endregion

    #region methods

    def _main(self):
        try:
            print("Retrieving log data")
            cryptos = self.__getalllogentries()
            print("Creating plot(s)")
            for _i in range(len(cryptos)):
                _crypto = cryptos[_i]
                print(f"  {_crypto.crypto} ({(_i + 1)}/{len(cryptos)})")
                self.__create_plot(_crypto)
        except helper.CLIError as _e:
            print(f"ERROR: {_e}", file = sys.stderr)
            return 1
        return 0

    #endregion

if __name__ == "__main__":
    sys.exit(Cmd().execute(sys.argv))
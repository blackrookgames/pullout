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

TItem = TypeVar('TItem')
TValue = TypeVar('TValue')

#region helper functions

def parse_path(input:str):
    try: path = Path(input)
    except:
        print(f"\"{input}\" is not a valid path.", file = sys.stderr)
        return False, None
    return True, path

def parse_date(input:str):
    dformat = input.\
        replace("YYYY", "{0:04}").\
        replace("YY", "{1:02}").\
        replace("MM", "{2:02}").\
        replace("DD", "{3:02}")
    return True, dformat

#endregion

class Cmd(cli.CLICommand):

    @property
    def _desc(self):
        return "Plot data from log files"

    #region input

    __crypto = cli.CLIRequiredDef(\
        name = "crypto",\
        desc = "Cryptocurrency to plot")
    __directory = cli.CLIRequiredDef(\
        name = "directory",\
        desc = "Input directory; this is where the log files are stored",\
        parse = parse_path)
    __output = cli.CLIRequiredDef(\
        name = "output",\
        desc = "Path of output file (*.png)",\
        parse = parse_path)
    
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
        parse = parse_date,\
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
    def __loopthrudir(cls, path:Path):
        try:
            for _path in path.iterdir():
                yield _path
            return
        except Exception as _e: e = helper.CLIError(_e)
        raise e

    @classmethod
    def __loopthrulog(cls, path:Path, crypto:str):
        try: data = ioutil.IOStrUtil.safestrs_from_file(path)
        except helper.CLIError: return
        offset = 0
        # Read number of columns
        try:
            columns = int(data[offset])
            offset += 1
        except: return
        # Find column of desired crypto
        try:
            column = -1
            for _i in range(columns):
                _crypto = data[offset]
                offset += 1
                if _crypto == crypto: column = _i # Do NOT break
            if column == -1: return
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
            # Price
            try:
                _price = float(data[offset + column])
                offset += columns
            except: return
            # Yield
            yield (_dt, _price)
    
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

    #endregion

    #region methods

    def _main(self):
        try:
            self_crypto = cast(str, self.crypto) # type: ignore
            self_directory = cast(Path, self.directory) # type: ignore
            self_output = cast(Path, self.output) # type: ignore
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
            # Loop thru log files
            print("Retrieving log data")
            entries:list[tuple[int, float]] = []
            for _path in self.__loopthrudir(self_directory):
                if not _path.is_file(): continue
                if not str(_path).endswith(".bin"): continue
                entries.extend(self.__loopthrulog(_path, self_crypto))
            if len(entries) < 2:
                raise helper.CLIError("Cannot create a graph with less than 2 entries.")
            entries.sort(key = lambda _entry: _entry[0])
            # Compute X-spacing
            print("Computing X-spacing")
            x_spaces = 25 if (self_x_spaces <= 0) else self_x_spaces
            x_pixels = 32 if (self_x_pixels <= 0) else self_x_pixels
            x_minmax = self.__compute_minmax(lambda t: t[0], entries)
            assert x_minmax is not None
            x_ups = self.__compute_ups(lambda v: int(v), x_minmax[0], x_minmax[1], x_spaces, 1)
            x_spaces = self.__compute_spaces(x_minmax[0], x_minmax[1], x_ups)
            x_p0 = int(math.floor(x_minmax[0] / x_ups) * x_ups)
            x_p1 = x_p0 + x_spaces * x_ups
            # Compute Y-spacing
            print("Computing Y-spacing")
            y_spaces = 15 if (self_y_spaces <= 0) else self_y_spaces
            y_pixels = 32 if (self_y_pixels <= 0) else self_y_pixels
            y_minmax = self.__compute_minmax(lambda t: t[1], entries)
            assert y_minmax is not None
            y_ups = self.__compute_ups(lambda v: int(v), y_minmax[0], y_minmax[1], y_spaces, 0.00001)
            y_spaces = self.__compute_spaces(y_minmax[0], y_minmax[1], y_ups)
            y_p0 = math.floor(y_minmax[0] / y_ups) * y_ups
            y_p1 = y_p0 + y_spaces * y_ups
            # Create image
            plot_x = 0
            plot_y = 0
            plot_w = x_pixels * x_spaces + 1 # Including border
            plot_h = y_pixels * y_spaces + 1 # Including border
            image = Image.new('RGBA', (plot_w, plot_h))
            color_bg = self.__from_rgba(self_color_bg)
            color_grid = self.__from_rgba(self_color_grid)
            color_plot = self.__from_rgba(self_color_plot)
            color_text = self.__from_rgba(self_color_text)
            # Draw grid lines
            print("Drawing grid lines")
            for _y in range(plot_h):
                _y_line = (_y % y_pixels) == 0
                for _x in range(plot_w):
                    image.putpixel((plot_x + _x, plot_y + _y),\
                        color_grid if (_y_line or (_x % x_pixels) == 0) else color_bg)
            # Plot data
            print("Plotting data")
            _i = 0
            _entry0 = entries[_i]
            _entry1 = entries[_i + 1]
            _prev_x = None
            _prev_y = None
            for _ox in range(plot_w):
                _ix = round(self.__lerp(x_p0, x_p1, _ox / (plot_w - 1)))
                # Compute y-input
                _iy = None
                if _ix >= _entry0[0]:
                    while True:
                        if _ix >= _entry1[0]:
                            if (_i + 2) >= len(entries):
                                break
                            _i += 1
                            _entry0 = entries[_i]
                            _entry1 = entries[_i + 1]
                            continue
                        _iy = self.__lerp(_entry0[1], _entry1[1], self.__invlerp(_entry0[0], _entry1[0], _ix))
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
            # Save image
            print("Saving image")
            self.__save_image(image, self_output)
        except helper.CLIError as _e:
            print(f"ERROR: {_e}", file = sys.stderr)
            return 1
        return 0

    #endregion

if __name__ == "__main__":
    sys.exit(Cmd().execute(sys.argv))
# import math
# import numpy as np
# import sys
# 
# from datetime import datetime
# from pathlib import Path
# from PIL import Image
# from typing import cast
# 
# import cry
# import engine.app as app
# import engine.boacon as boacon
# import engine.cli as cli
# import engine.helper as helper
# import engine.ioutil as ioutil
# import entity
# 
# #region helper functions
# 
# def parse_path(input:str):
#     try: path = Path(input)
#     except:
#         print(f"\"{input}\" is not a valid path.", file = sys.stderr)
#         return False, None
#     return True, path
# 
# def parse_date(input:str):
#     dformat = input.\
#         replace("YYYY", "{0:04}").\
#         replace("YY", "{1:02}").\
#         replace("MM", "{2:02}").\
#         replace("DD", "{3:02}")
#     return True, dformat
# 
# #endregion
# 
# class Cmd(cli.CLICommand):
# 
#     @property
#     def _desc(self):
#         return "Plot data from log files"
# 
#     #region input
# 
#     __crypto = cli.CLIRequiredDef(\
#         name = "crypto",\
#         desc = "Cryptocurrency to plot")
#     __directory = cli.CLIRequiredDef(\
#         name = "directory",\
#         desc = "Input directory; this is where the log files are stored",\
#         parse = parse_path)
#     __output = cli.CLIRequiredDef(\
#         name = "output",\
#         desc = "Path of output file (*.png)",\
#         parse = parse_path)
#     
#     __x_time = cli.CLIOptionWArgDef(\
#         name = "x_time",\
#         desc = "Length of time (in seconds) per X-unit",\
#         parse = cli.CLIParseUtil.to_float,\
#         default = 0.0)
#     __x_pixels = cli.CLIOptionWArgDef(\
#         name = "x_pixels",\
#         desc = "Pixels per X-unit",\
#         parse = cli.CLIParseUtil.to_int,\
#         default = 0)
#     __y_price = cli.CLIOptionWArgDef(\
#         name = "y_price",\
#         desc = "Price difference per Y-unit",\
#         parse = cli.CLIParseUtil.to_float,\
#         default = 0.0)
#     __y_pixels = cli.CLIOptionWArgDef(\
#         name = "y_pixels",\
#         desc = "Pixels per Y-unit",\
#         parse = cli.CLIParseUtil.to_int,\
#         default = 0)
#     
#     __date = cli.CLIOptionWArgDef(\
#         name = "date",\
#         desc = "Date format (ex: MM/DD/YY, DD/MM/YYYY, YY/MM/DD)",\
#         parse = parse_date,\
#         default = "MM/DD/YYYY")
#     __time12 = cli.CLIOptionFlagDef(\
#         name = "time12",\
#         desc = "If specified, time is displayed in a 12-hour format")
# 
#     #endregion
# 
#     #region helper methods
# 
#     @classmethod
#     def __loopthrudir(cls, path:Path):
#         try:
#             for _path in path.iterdir():
#                 yield _path
#             return
#         except Exception as _e: e = helper.CLIError(_e)
#         raise e
# 
#     @classmethod
#     def __loopthrulog(cls, path:Path, crypto:str):
#         try: data = ioutil.IOStrUtil.safestrs_from_file(path)
#         except helper.CLIError: return
#         offset = 0
#         # Read number of columns
#         try:
#             columns = int(data[offset])
#             offset += 1
#         except: return
#         # Find column of desired crypto
#         try:
#             column = -1
#             for _i in range(columns):
#                 _crypto = data[offset]
#                 offset += 1
#                 if _crypto == crypto: column = _i # Do NOT break
#             if column == -1: return
#         except: return
#         # Loop thru entries
#         for _i in range((len(data) - offset) // (columns + 1)):
#             # Date/time
#             try:
#                 _rawdt = data[offset]
#                 _dt = helper.DTUtil.to_micro2000(datetime(\
#                     int(_rawdt[:4]), int(_rawdt[4:6]), int(_rawdt[6:8]),\
#                     hour = int(_rawdt[8:10]), minute = int(_rawdt[10:12]),\
#                     second = int(_rawdt[12:14]), microsecond = int(_rawdt[14:20])))
#                 offset += 1
#             except: return
#             # Price
#             try:
#                 _price = float(data[offset + column])
#                 offset += columns
#             except: return
#             # Yield
#             yield (_dt, _price)
#     
#     @classmethod
#     def __from_micro(cls, microseconds:int):
#         return microseconds / 1000000
# 
#     @classmethod
#     def __to_micro(cls, seconds:float):
#         if seconds >= 0.0:
#             return int(math.floor(seconds * 1000000))
#         return -int(math.floor((-seconds) * 1000000))
# 
#     @classmethod
#     def __save_image(cls, image:Image.Image, path:Path):
#         try:
#             image.save(path)
#             return
#         except Exception as _e: e = helper.CLIError(_e)
#         raise e
# 
#     #endregion
# 
#     #region methods
# 
#     def _main(self):
#         try:
#             self_crypto = cast(str, self.crypto) # type: ignore
#             self_directory = cast(Path, self.directory) # type: ignore
#             self_output = cast(Path, self.output) # type: ignore
#             self_x_time = cast(float, self.x_time) # type: ignore
#             self_x_pixels = cast(int, self.x_pixels) # type: ignore
#             self_y_price = cast(float, self.y_price) # type: ignore
#             self_y_pixels = cast(int, self.y_pixels) # type: ignore
#             self_date = cast(str, self.date) # type: ignore
#             self_time12 = cast(bool, self.time12) # type: ignore
#             # Get date/time format
#             dtformat = helper.DTFormat(self_date, self_time12)
#             # Loop thru log files
#             print("Retrieving log data")
#             entries:list[tuple[int, float]] = []
#             for _path in self.__loopthrudir(self_directory):
#                 if not _path.is_file(): continue
#                 if not str(_path).endswith(".bin"): continue
#                 entries.extend(self.__loopthrulog(_path, self_crypto))
#             if len(entries) < 2:
#                 raise helper.CLIError("Cannot create a graph with less than 2 entries.")
#             entries.sort(key = lambda _entry: _entry[0])
#             # Compute time per X-unit
#             if self_x_time > 0.0:
#                 x_time_ms = self.__to_micro(self_x_time)
#             else:
#                 # Compute range
#                 _min = entries[0][0]
#                 _max = entries[0][0]
#                 for _i in range(1, len(entries)):
#                     _dt = entries[_i][0]
#                     if _max < _dt: _max = _dt
#                     if _min > _dt: _min = _dt
#                 _range = _max - _min
#                 # Find "capturing" "base 10" number
#                 _capture = 100
#                 while _range > _capture:
#                     _capture *= 100
#                 # Determine a price per Y-unit
#                 x_time_ms = _capture // 1000
#             # Compute pixels per X-unit
#             x_pixels = 16 if (self_x_pixels <= 0) else self_x_pixels
#             # Compute price per Y-unit
#             y_price = self_y_price
#             if y_price <= 0.0:
#                 # Compute range
#                 _min = entries[0][1]
#                 _max = entries[0][1]
#                 for _i in range(1, len(entries)):
#                     _price = entries[_i][1]
#                     if _max < _price: _max = _price
#                     if _min > _price: _min = _price
#                 _range = _max - _min
#                 # Find "capturing" "base 10" number
#                 _capture = 1
#                 while _range > _capture:
#                     _capture *= 10.0
#                 # Determine a price per Y-unit
#                 y_price = _capture / 10.0
#             # Compute pixels per Y-unit
#             y_pixels = 16 if (self_y_pixels <= 0) else self_y_pixels
#             # Compute ranges
#             _entry = entries[0]
#             dt_min = _entry[0]
#             dt_max = dt_min
#             pr_min = _entry[1]
#             pr_max = pr_min
#             for _i in range(len(entries)):
#                 _entry = entries[_i]
#                 if dt_min > _entry[0]: dt_min = _entry[0]
#                 if dt_max < _entry[0]: dt_max = _entry[0]
#                 if pr_min > _entry[1]: pr_min = _entry[1]
#                 if pr_max < _entry[1]: pr_max = _entry[1]
#             dt_min = (dt_min // x_time_ms) * x_time_ms
#             dt_max = ((dt_max + x_time_ms - 1) // x_time_ms) * x_time_ms
#             pr_min = math.floor(pr_min / y_price) * y_price
#             pr_max = math.ceil(pr_max / y_price) * y_price
#             dt_range = dt_max - dt_min
#             dt_units = dt_range // x_time_ms
#             pr_range = pr_max - pr_min
#             pr_units = int(pr_range / y_price)
#             # Begin creating plot buffer
#             print("Creating plot buffer")
#             plot_w = dt_units * x_pixels + 1 # Extra pixel for border
#             plot_h = pr_units * y_pixels + 1 # Extra pixel for border
#             plot = np.zeros([plot_w, plot_h], dtype = np.uint32)
#             # Add grid spaces
#             print("  Adding grid spaces")
#             GRID_COLOR = 0x808080FF
#             for _x in range(0, plot_w, x_pixels):
#                 for _y in range(plot_h):
#                     plot[_x, _y] = GRID_COLOR
#             for _y in range(0, plot_h, y_pixels):
#                 for _x in range(plot_w):
#                     plot[_x, _y] = GRID_COLOR
#             # Create image
#             print("  Creating final image")
#             _image = Image.new('RGBA', (plot_w, plot_h))
#             for _y in range(plot_h):
#                 for _x in range(plot_w):
#                     _p = plot[_x, _y]
#                     _r = 0xFF & (_p >> 24)
#                     _g = 0xFF & (_p >> 16)
#                     _b = 0xFF & (_p >> 8)
#                     _a = 0xFF & _p
#                     _image.putpixel((_x, _y), (_r, _g, _b, _a))
#             self.__save_image(_image, self_output)
#         except helper.CLIError as _e:
#             print(f"ERROR: {_e}", file = sys.stderr)
#             return 1
#         return 0
# 
#     #endregion
# 
# if __name__ == "__main__":
#     sys.exit(Cmd().execute(sys.argv))
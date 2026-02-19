# ------------------------------------------------------------------------->
import curses
import sys

from datetime import datetime
from pathlib import Path
from typing import cast

import cry
import engine.app as app
import engine.boacon as boacon
import engine.cli as cli
import engine.helper as helper
import entity

#region helper functions

def parse_symbols(input:str):
    symbols:dict[str, str] = {}
    for _rawsymbol in input.split(','):
        _symbol = _rawsymbol.strip() 
        if len(_symbol) == 0: continue
        # Find slash
        if not ('/' in _symbol):
            print(f"ERROR: Missing forward slash: {_symbol}",\
                file = sys.stderr)
            return False, None
        _slashpos = _symbol.index('/')
        # Add symbol
        symbols[_symbol[0:_slashpos]] = _symbol[(_slashpos + 1):]
    return True, symbols

def parse_list(input:str):
    newlist:list[str] = []
    for _item in input.split(','):
        __item = _item.strip()
        if len(__item) > 0: newlist.append(__item)
    return True, newlist

def parse_date(input:str):
    dformat = input.\
        replace("YYYY", "{0:04}").\
        replace("YY", "{1:02}").\
        replace("MM", "{2:02}").\
        replace("DD", "{3:02}")
    return True, dformat

#endregion

class Cmd(cli.CLICommand):

    #region init

    def __init__(self):
        super().__init__()
        # Visual offsets
        self.__vis_left = 0
        self.__vis_right = 0
        self.__vis_top = 0
        self.__vis_bottom = 0
        # Date/time format
        self.__datetime:None|helper.DTFormat = None

    #endregion

    #region input

    __symbols = cli.CLIOptionWArgDef(\
        name = "symbols",\
        short = 's',\
        desc = "Symbols (ex: BTC/USD)",\
        parse = parse_symbols,\
        default = None)
    __currency = cli.CLIOptionWArgDef(\
        name = "currency",\
        short = 'c',\
        desc = "Currency to convert crypto from/to (ex: USD)." +\
            " Ignored if --symbols is defined",\
        default = 'USD')
    __count = cli.CLIOptionWArgDef(\
        name = "count",\
        short = 'n',\
        desc = "Number of symbols to retrieve." +\
            " Ignored if --symbols is defined",\
        parse = cli.CLIParseUtil.to_int,\
        default = 10)
    
    __ex = cli.CLIOptionWArgDef(\
        name = "ex",\
        desc = "Crypto to exclude; " +\
            "non-crypto can also be included (such as USD)." +\
            " Ignored if --symbols is defined",\
        parse = parse_list,\
        default = None)
    
    __ex_pfx = cli.CLIOptionWArgDef(\
        name = "ex_pfx",\
        desc = "Prefixes of crypto to exclude; " +\
            "non-crypto can also be included (such as USD)." +\
            " Ignored if --symbols is defined",\
        parse = parse_list,\
        default = None)
    
    __interval = cli.CLIOptionWArgDef(\
        name = "interval",\
        desc = "Length of update intervals",\
        parse = cli.CLIParseUtil.to_float,\
        default = 1.0)
    
    __ddos_delay = cli.CLIOptionWArgDef(\
        name = "ddos_delay",\
        desc = "Delay after DDOS error",\
        parse = cli.CLIParseUtil.to_float,\
        default = 30.0)
    __ddos_max = cli.CLIOptionWArgDef(\
        name = "ddos_max",\
        desc = "Max retries after DDOS error",\
        parse = cli.CLIParseUtil.to_int,\
        default = 4)
    __net_delay = cli.CLIOptionWArgDef(\
        name = "net_delay",\
        desc = "Max retries after network error",\
        parse = cli.CLIParseUtil.to_float,\
        default = 5.0)
    __net_max = cli.CLIOptionWArgDef(\
        name = "net_max",\
        desc = "Delay after network error",\
        parse = cli.CLIParseUtil.to_int,\
        default = 40)
    
    __off_left = cli.CLIOptionWArgDef(\
        name = "off_left",\
        desc = "Visual offset of left edge",\
        parse = cli.CLIParseUtil.to_int,\
        default = 0)
    __off_right = cli.CLIOptionWArgDef(\
        name = "off_right",\
        desc = "Visual offset of right edge",\
        parse = cli.CLIParseUtil.to_int,\
        default = 0)
    __off_top = cli.CLIOptionWArgDef(\
        name = "off_top",\
        desc = "Visual offset of top edge",\
        parse = cli.CLIParseUtil.to_int,\
        default = 0)
    __off_bottom = cli.CLIOptionWArgDef(\
        name = "off_bottom",\
        desc = "Visual offset of bottom edge",\
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

    #endregion

    #region recievers

    def __r_boacon_on_init(self):
        boacon.postdraw().connect(self.__r_boacon_post_draw)

    def __r_boacon_on_final(self):
        boacon.postdraw().disconnect(self.__r_boacon_post_draw)

    def __r_boacon_post_draw(self, win:curses.window):
        assert self.__datetime is not None
        # Create string representation
        dtstr = self.__datetime.create(datetime.now())
        # Print
        try:
            h, w = win.getmaxyx()
            win.addstr(\
                h - self.__vis_bottom - 1,\
                w - self.__vis_right - len(dtstr),\
                dtstr)
        except curses.error: pass

    #endregion

    #region helper methods

    def __runapp(self,\
            crypto:cry.Cry,\
            crypto_opparams:cry.CryOpParams,\
            crypto_symbols:dict[str, str]):
        D_CONSOLE = 10
        assert self.__datetime is not None
        #region gather input
        self_interval = cast(float,\
            self.interval) # type: ignore
        #endregion
        params = app.AppStart()
        # Fix visual offsets
        panes_left = self.__vis_left + 1
        panes_right = self.__vis_right + 1
        panes_top = self.__vis_top + 1
        panes_bottom = self.__vis_bottom + 2
        # Fix crypto op params
        crypto_opparams = crypto_opparams.copy()
        crypto_opparams.printfunc = app.console().print
        # Create crypto handler
        obj_crypto = entity.CryptoStats(\
            crypto, crypto_symbols, crypto_opparams,\
            self_interval)
        params.objects.append(obj_crypto)
        # Create status table
        obj_statustable = entity.StatusTable(\
            obj_crypto, self.__datetime)
        obj_statustable.x.dis0 = panes_left
        obj_statustable.x.dis1 = panes_right
        obj_statustable.y.dis0 = panes_top
        obj_statustable.y.dis1 = panes_bottom + D_CONSOLE + 1
        params.objects.append(obj_statustable)
        # Setup console pane
        params.con_left = panes_left
        params.con_right = panes_right
        params.con_top = None
        params.con_bottom = panes_bottom
        params.con_height = D_CONSOLE
        # Run
        app.run(params)

    def __get_opparams(self):
        crypto_opparams = cry.CryOpParams()
        crypto_opparams.ddos_delay = cast(float,\
            self.ddos_delay) # type: ignore
        crypto_opparams.ddos_max = cast(int,\
            self.ddos_max) # type: ignore
        crypto_opparams.net_delay = cast(float,\
            self.net_delay) # type: ignore
        crypto_opparams.net_max = cast(int,\
            self.net_max) # type: ignore
        return crypto_opparams

    def __get_symbols(self,\
            crypto:cry.Cry,\
            crypto_opparams:cry.CryOpParams):
        symbols = cast(None|dict[str, str],\
            self.symbols) # type: ignore
        if symbols is None:
            self_currency = cast(str,\
                self.currency) # type: ignore
            self_count = cast(int,\
                self.count) # type: ignore
            # Get exclusions
            ex = cast(None|list[str],\
                self.ex) # type: ignore
            ex_pfx = cast(None|list[str],\
                self.ex_pfx) # type: ignore
            if ex is None: ex:list[str] = []
            if ex_pfx is None: ex_pfx:list[str] = []
            # Retrieve all symbols
            _allsymbols = crypto.get_symbols(\
                opparams = crypto_opparams)
            # Extract requested symbols
            symbols = {}
            for _rawsymbol in _allsymbols:
                # Check if all requested symbols have been retrieved
                if len(symbols) >= self_count: break
                # Find slash
                _slash = -1
                for _i in range(len(_rawsymbol)):
                    if _rawsymbol[_i] != '/': continue
                    _slash = _i
                    break
                if _slash == -1: continue
                # Get crypto
                _crypto = cast(str, _rawsymbol[:_slash])
                if _crypto in symbols: continue
                # Get currency
                _currency = cast(str, _rawsymbol[(_slash + 1):])
                if _currency != self_currency: continue
                # Check if crypto is excluded
                _excluded = False
                for _ex in ex:
                    if _crypto != _ex: continue
                    _excluded = True
                    break
                for _ex_pfx in ex_pfx:
                    if not _crypto.startswith(_ex_pfx): continue
                    _excluded = True
                    break
                if _excluded: continue
                # Add symbol
                symbols[_crypto] = _currency
        return symbols
    
    #endregion

    #region methods

    def _main(self):
        try:
            # Update offsets
            self_off_left = cast(int,\
                self.off_left) # type: ignore
            self_off_right = cast(int,\
                self.off_right) # type: ignore
            self_off_top = cast(int,\
                self.off_top) # type: ignore
            self_off_bottom = cast(int,\
                self.off_bottom) # type: ignore
            self.__vis_left = max(0, self_off_left)
            self.__vis_right = max(0, self_off_right)
            self.__vis_top = max(0, self_off_top)
            self.__vis_bottom = max(0, self_off_bottom)
            # Get date/time format
            self_date = cast(str, self.date) # type: ignore
            self_time12 = cast(bool, self.time12) # type: ignore
            self.__datetime = helper.DTFormat(self_date, self_time12)
            # Get crypto operation arguments
            crypto_opparams = self.__get_opparams()
            # Load API
            print("Loading API")
            crypto_api = cry.CryAPI(Path(sys.argv[0]).resolve()\
                .parent\
                .joinpath("secret")\
                .joinpath("cdp_api_key.json"))
            # Create exchange instance
            print("Creating exchange instance")
            crypto = cry.Cry(crypto_api)
            # Load market
            print("Loading market")
            crypto.load_markets(opparams = crypto_opparams)
            # Retrieve symbols
            print("Retrieving symbols")
            crypto_symbols = self.__get_symbols(\
                crypto, crypto_opparams)
            # Connect signals
            boacon.on_init().connect(self.__r_boacon_on_init)
            boacon.on_final().connect(self.__r_boacon_on_final)
            # Run main app code
            print("Launching app")
            self.__runapp(crypto, crypto_opparams, crypto_symbols)
        except helper.CLIError as _e:
            print(f"ERROR: {_e}", file = sys.stderr)
            return 1
        return 0

    #endregion

if __name__ == "__main__":
    sys.exit(Cmd().execute(sys.argv))
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

def parse_set(input:str):
    newset:set[str] = set()
    for _item in input.split(','):
        __item = _item.strip()
        if len(__item) == 0: continue
        if __item in newset: continue
        newset.add(__item)
    return True, newset

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
        # App objects
        self.__obj_miscops:None|entity.MiscOps = None
        self.__obj_keeper:None|entity.CryptoKeeper = None
        self.__obj_table:None|entity.StatusTable = None
        self.__obj_buysell:None|entity.BuySell = None
        self.__obj_settingsview:None|entity.StaticTableView = None
        self.__obj_keycontrols:None|entity.KeyControls = None
        # Print cache
        self.__printcache = []

    #endregion

    #region input

    __crypto = cli.CLIOptionWArgDef(\
        name = "crypto",\
        short = 'b',\
        desc = "Crypto currencies to invest in (ex: BTC)",\
        parse = parse_set,\
        default = None)
    __currency = cli.CLIOptionWArgDef(\
        name = "currency",\
        short = 'c',\
        desc = "Currency to convert crypto from/to (ex: USD).",\
        default = 'USD')
    __count = cli.CLIOptionWArgDef(\
        name = "count",\
        short = 'n',\
        desc = "Number of crypto currencies to retrieve." +\
            " Ignored if --crypto is defined",\
        parse = cli.CLIParseUtil.to_int,\
        default = 10)
    
    __ex = cli.CLIOptionWArgDef(\
        name = "ex",\
        desc = "Crypto currencies to exclude; " +\
            "non-crypto can also be included (such as USD)." +\
            " Ignored if --crypto is defined",\
        parse = parse_list,\
        default = None)
    
    __ex_pfx = cli.CLIOptionWArgDef(\
        name = "ex_pfx",\
        desc = "Prefixes of crypto currencies to exclude; " +\
            "non-crypto can also be included (such as USD)." +\
            " Ignored if --crypto is defined",\
        parse = parse_list,\
        default = None)
    
    __sellall = cli.CLIOptionFlagDef(\
        name = "sellall",\
        desc = "Whether or not to sell all existing crypto")
    
    __interval = cli.CLIOptionWArgDef(\
        name = "interval",\
        desc = "Length of update intervals",\
        parse = cli.CLIParseUtil.to_float,\
        default = 1.0)
    
    __date = cli.CLIOptionWArgDef(\
        name = "date",\
        desc = "Date format (ex: MM/DD/YY, DD/MM/YYYY, YY/MM/DD)",\
        parse = parse_date,\
        default = "MM/DD/YYYY")
    __time12 = cli.CLIOptionFlagDef(\
        name = "time12",\
        desc = "If specified, time is displayed in a 12-hour format")

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

    #endregion

    #region recievers

    def __r_boacon_on_init(self):
        # Connect signals
        boacon.postdraw().connect(self.__r_boacon_post_draw)
        # Set nav controls for settings view
        assert self.__obj_settingsview is not None        
        self.__obj_settingsview.nav_up = curses.KEY_LEFT    
        self.__obj_settingsview.nav_down = curses.KEY_RIGHT

    def __r_boacon_on_final(self):
        # Disconnect signals
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

    def __r_obj_miscops_prompt_finish(self):
        for _text in self.__printcache:
            app.console().print(_text)
        self.__printcache.clear()

    #endregion

    #region helper methods

    def __print(self, text:str):
        assert self.__obj_miscops is not None
        if self.__obj_miscops.prompting:
            self.__printcache.append(text)
        else: app.console().print(text)

    def __get_cryptocurrs(self,\
            cryp:cry.Cry,\
            cryp_opparams:cry.CryOpParams):
        crypto = cast(None|set[str], self.crypto) # type: ignore
        if crypto is None:
            self_currency = cast(str, self.currency) # type: ignore
            self_count = cast(int, self.count) # type: ignore
            # Get exclusions
            ex = cast(None|list[str], self.ex) # type: ignore
            ex_pfx = cast(None|list[str], self.ex_pfx) # type: ignore
            if ex is None: ex:list[str] = []
            if ex_pfx is None: ex_pfx:list[str] = []
            # Retrieve all symbols
            _allsymbols = cryp.get_symbols(opparams = cryp_opparams)
            # Extract requested symbols
            crypto = set()
            for _rawsymbol in _allsymbols:
                # Check if all requested symbols have been retrieved
                if len(crypto) >= self_count: break
                # Find slash
                _slash = -1
                for _i in range(len(_rawsymbol)):
                    if _rawsymbol[_i] != '/': continue
                    _slash = _i
                    break
                if _slash == -1: continue
                # Get crypto
                _crycur = cast(str, _rawsymbol[:_slash])
                if _crycur in crypto: continue
                # Get currency
                _currency = cast(str, _rawsymbol[(_slash + 1):])
                if _currency != self_currency: continue
                # Check if crypto is excluded
                _excluded = False
                for _ex in ex:
                    if _crycur != _ex: continue
                    _excluded = True
                    break
                for _ex_pfx in ex_pfx:
                    if not _crycur.startswith(_ex_pfx): continue
                    _excluded = True
                    break
                if _excluded: continue
                # Add crypto
                crypto.add(_crycur)
        return crypto
    
    #endregion

    #region methods

    def _main(self):
        D_CONSOLE = 10
        D_STATUS = 50
        D_BUYSELL = 30
        D_KEYCONTROLS = 20
        try:
            self_currency = cast(str, self.currency) # type: ignore
            self_sellall = cast(bool, self.sellall) # type: ignore
            self_interval = cast(float, self.interval) # type: ignore
            self_date = cast(str, self.date) # type: ignore
            self_time12 = cast(bool, self.time12) # type: ignore
            self_ddos_delay = cast(float, self.ddos_delay) # type: ignore
            self_ddos_max = cast(int, self.ddos_max) # type: ignore
            self_net_delay = cast(float, self.net_delay) # type: ignore
            self_net_max = cast(int, self.net_max) # type: ignore
            self_off_left = cast(int, self.off_left) # type: ignore
            self_off_right = cast(int, self.off_right) # type: ignore
            self_off_top = cast(int, self.off_top) # type: ignore
            self_off_bottom = cast(int, self.off_bottom) # type: ignore
            # Update offsets
            self.__vis_left = max(0, self_off_left)
            self.__vis_right = max(0, self_off_right)
            self.__vis_top = max(0, self_off_top)
            self.__vis_bottom = max(0, self_off_bottom)
            # Get date/time format
            self.__datetime = helper.DTFormat(self_date, self_time12)
            # Get crypto operation arguments
            crypto_opparams = cry.CryOpParams()
            crypto_opparams.ddos_delay = self_ddos_delay
            crypto_opparams.ddos_max = self_ddos_max
            crypto_opparams.net_delay = self_net_delay
            crypto_opparams.net_max = self_net_max
            # Load API
            print("Loading API")
            crypto_api = cry.CryAPI(Path(sys.argv[0]).resolve()\
                .parent.joinpath("secret").joinpath("cdp_api_key.json"))
            # Create exchange instance
            print("Creating exchange instance")
            crypto = cry.Cry(crypto_api)
            # Load market
            print("Loading market")
            crypto.load_markets(opparams = crypto_opparams)
            # Retrieve symbols
            print("Retrieving symbols")
            crypto_cryptocurrs = self.__get_cryptocurrs(crypto, crypto_opparams)
            # Sell all crypto (if requested)
            if self_sellall:
                print("Selling existing crypto")
                # Fetch balance
                _balance = crypto.fetch_balance(opparams = crypto_opparams)
                # Loop thru free
                for _k, _v in _balance["free"].items():
                    # Make sure currency is crypto
                    if _k == self_currency: continue
                    # Make sure there's a balance
                    _bal = float(_v) # type: ignore
                    if _bal <= 0.0: continue
                    # Sell
                    try:
                        crypto.order_sell(f"{_k}/{self_currency}", _bal)
                        continue
                    except helper.CLIError as _e:
                        if _e.etype == helper.CLIErrorType.PRECISION:
                            continue
                        _ex = _e
                    raise _ex
            # Connect signals
            boacon.on_init().connect(self.__r_boacon_on_init)
            boacon.on_final().connect(self.__r_boacon_on_final)
            params = app.AppStart()
            # Fix visual offsets
            panes_left = self.__vis_left + 1
            panes_right = self.__vis_right + 1
            panes_top = self.__vis_top + 1
            panes_bottom = self.__vis_bottom + 2
            # Fix crypto op params
            crypto_opparams = crypto_opparams.copy()
            crypto_opparams.printfunc = self.__print
            # Create misc operation handler
            self.__obj_miscops = entity.MiscOps()
            self.__obj_miscops.prompt_finish.connect(self.__r_obj_miscops_prompt_finish)
            params.objects.append(self.__obj_miscops)
            # Create crypto keeper
            self.__obj_keeper = entity.CryptoKeeper(\
                crypto, crypto_opparams,\
                crypto_cryptocurrs, self_currency,\
                self_interval)
            params.objects.append(self.__obj_keeper)
            # Create table
            self.__obj_table = entity.StatusTable(self.__obj_keeper, self.__datetime)
            self.__obj_table.x.dis0 = panes_left
            self.__obj_table.x.len = D_STATUS
            self.__obj_table.y.dis0 = panes_top
            self.__obj_table.y.dis1 = panes_bottom + D_CONSOLE + 1
            params.objects.append(self.__obj_table)
            # Create buy/sell handler
            self.__obj_buysell = entity.BuySell(crypto, crypto_opparams, self.__obj_keeper, self.__obj_table)
            self.__obj_buysell.x.dis0 = panes_left + D_STATUS + 1
            self.__obj_buysell.x.len = D_BUYSELL
            self.__obj_buysell.y.dis0 = panes_top
            self.__obj_buysell.y.dis1 = panes_bottom + D_CONSOLE + 1
            params.objects.append(self.__obj_buysell)
            # Create settings view
            _settingsview_rows = [\
                [ " Interval", f"{self_interval} sec" ],\
                [ " Date Format", self_date ],\
                [ " 12 Hours", self_time12 ],\
                [ " DDOS Delay", f"{self_ddos_delay} sec" ],\
                [ " DDOS Max", f"{self_ddos_max} {("retries" if (self_ddos_max != 1) else "retry")}" ],\
                [ " Net Delay", f"{self_net_delay} sec" ],\
                [ " Net Max", f"{self_net_max} {("retries" if (self_net_max != 1) else "retry")}" ],]
            self.__obj_settingsview = entity.StaticTableView([ 20, 100 ], rows = _settingsview_rows)
            self.__obj_settingsview.x.dis0 = panes_left + D_STATUS + 1 + D_BUYSELL + 1
            self.__obj_settingsview.x.dis1 = panes_right
            self.__obj_settingsview.y.dis0 = panes_top
            self.__obj_settingsview.y.dis1 = panes_bottom + D_CONSOLE + 1
            params.objects.append(self.__obj_settingsview)
            # Create keyboard control display
            self.__obj_keycontrols = entity.KeyControls()
            self.__obj_keycontrols.x.len = D_KEYCONTROLS
            self.__obj_keycontrols.x.dis1 = panes_right
            self.__obj_keycontrols.y.len = D_CONSOLE
            self.__obj_keycontrols.y.dis1 = panes_bottom
            params.objects.append(self.__obj_keycontrols)
            # Setup console pane
            params.con_left = panes_left
            params.con_right = panes_right + D_KEYCONTROLS + 1
            params.con_top = None
            params.con_bottom = panes_bottom
            params.con_height = D_CONSOLE
            # Run main app code
            print("Launching app")
            app.run(params)
        except helper.CLIError as _e:
            print(f"ERROR: {_e}", file = sys.stderr)
            return 1
        return 0

    #endregion

if __name__ == "__main__":
    sys.exit(Cmd().execute(sys.argv))
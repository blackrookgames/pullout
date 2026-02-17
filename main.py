# ------------------------------------------------------------------------->
import sys

from pathlib import Path
from typing import cast

import engine.app as app
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

#endregion

class Cmd(cli.CLICommand):

    #region input

    __symbols = cli.CLIRequiredDef(\
        name = "symbols",\
        desc = "Symbols (ex: BTC/USD)",\
        parse = parse_symbols)
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

    #endregion

    #region methods

    def _main(self):
        D_CONSOLE = 6
        #region gather input
        self_symbols = cast(dict[str, str],\
            self.symbols) # type: ignore
        self_interval = cast(float,\
            self.interval) # type: ignore
        self_ddos_delay = cast(float,\
            self.ddos_delay) # type: ignore
        self_ddos_max = cast(int,\
            self.ddos_max) # type: ignore
        self_net_delay = cast(float,\
            self.net_delay) # type: ignore
        self_net_max = cast(int,\
            self.net_max) # type: ignore
        self_off_left = cast(int,\
            self.off_left) # type: ignore
        self_off_right = cast(int,\
            self.off_right) # type: ignore
        self_off_top = cast(int,\
            self.off_top) # type: ignore
        self_off_bottom = cast(int,\
            self.off_bottom) # type: ignore
        #endregion
        try:
            params = app.AppStart()
            params.apipath = Path(sys.argv[0]).resolve()\
                .parent\
                .joinpath("secret")\
                .joinpath("cdp_api_key.json")
            # Fix visual offsets
            fix_left = self_off_left + 1
            fix_right = self_off_right + 1
            fix_top = self_off_top + 1
            fix_bottom = self_off_bottom + 1
            # Create crypto handler
            obj_crypto = entity.CryptoStats(\
                self_symbols, self_interval,\
                self_ddos_delay, self_ddos_max,\
                self_net_delay, self_net_max)
            params.objects.append(obj_crypto)
            # Create status table
            obj_statustable = entity.StatusTable(obj_crypto)
            obj_statustable.x.dis0 = fix_left
            obj_statustable.x.dis1 = fix_right
            obj_statustable.y.dis0 = fix_top
            obj_statustable.y.dis1 = fix_bottom + D_CONSOLE + 1
            params.objects.append(obj_statustable)
            # Setup console pane
            params.con_left = fix_left
            params.con_right = fix_right
            params.con_top = None
            params.con_bottom = fix_bottom
            params.con_height = D_CONSOLE
            # Run
            app.run(params)
        except helper.CLIError as _e:
            print(f"ERROR: {_e}", file = sys.stderr)
            return 1
        return 0

    #endregion

if __name__ == "__main__":
    sys.exit(Cmd().execute(sys.argv))
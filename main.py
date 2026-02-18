# ------------------------------------------------------------------------->
import sys

from pathlib import Path
from typing import cast

import cry
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

    #region helper methods

    def __runapp(self,\
            crypto:cry.Cry,\
            crypto_opparams:cry.CryOpParams,\
            crypto_symbols:dict[str, str]):
        D_CONSOLE = 10
        #region gather input
        self_interval = cast(float,\
            self.interval) # type: ignore
        self_off_left = cast(int,\
            self.off_left) # type: ignore
        self_off_right = cast(int,\
            self.off_right) # type: ignore
        self_off_top = cast(int,\
            self.off_top) # type: ignore
        self_off_bottom = cast(int,\
            self.off_bottom) # type: ignore
        #endregion
        params = app.AppStart()
        # Fix visual offsets
        fix_left = self_off_left + 1
        fix_right = self_off_right + 1
        fix_top = self_off_top + 1
        fix_bottom = self_off_bottom + 1
        # Fix crypto op params
        crypto_opparams = crypto_opparams.copy()
        crypto_opparams.printfunc = app.console().print
        # Create crypto handler
        obj_crypto = entity.CryptoStats(\
            crypto, crypto_symbols, crypto_opparams,\
            self_interval)
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
                _crypto = _rawsymbol[:_slash]
                if _crypto in symbols: continue
                # Get currency
                _currency = _rawsymbol[(_slash + 1):]
                if _currency != self_currency: continue
                # Add symbol
                symbols[_crypto] = _currency
        return symbols
    
    #endregion

    #region methods

    def _main(self):
        try:
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
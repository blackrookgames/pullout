# ------------------------------------------------------------------------->
import asyncio
import pathlib
import sys

from typing import cast

import src

async def loop(app:src.App):
    looping = True
    error = None
    loop = asyncio.get_running_loop()
    update_params = src.AppUpdateParams()
    update_result = src.AppUpdateResult() # Trick the loop so an initial update will be triggered
    update_lptime = loop.time()
    while looping:
        # Input
        _key = app.appio.get_ch()
        if _key != -1: update_params.input_add(_key)
        # Update
        if update_result is not None:
            # Get delta
            _start = update_lptime
            update_lptime = loop.time()
            update_params.delta = update_lptime - _start
            # Evaluate result
            if update_result.error is not None:
                error = update_result.error
                looping = False
            elif app.quit:
                looping = False
            # Schedule next update
            if looping:
                _task = loop.run_in_executor(None, app.update, update_params)
                async def wait_task():
                    nonlocal update_result
                    update_result = await _task
                asyncio.create_task(wait_task())
                update_params = src.AppUpdateParams()
                update_result = None
        # Yield control
        await asyncio.sleep(0.01)
    if error is None: return
    raise error

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

class Cmd(src.CLICommand):
    __symbols = src.CLIRequiredDef(\
        name = "symbols",\
        desc = "Symbols (ex: BTC/USD)",\
        parse = parse_symbols)
    __ddos_delay = src.CLIOptionWArgDef(\
        name = "ddos_delay",\
        desc = "Delay after DDOS error",\
        parse = src.CLIParseUtil.to_float,\
        default = 30.0)
    __ddos_max = src.CLIOptionWArgDef(\
        name = "ddos_max",\
        desc = "Max retries after DDOS error",\
        parse = src.CLIParseUtil.to_int,\
        default = 4)
    __net_delay = src.CLIOptionWArgDef(\
        name = "net_delay",\
        desc = "Max retries after network error",\
        parse = src.CLIParseUtil.to_float,\
        default = 5.0)
    __net_max = src.CLIOptionWArgDef(\
        name = "net_max",\
        desc = "Delay after network error",\
        parse = src.CLIParseUtil.to_int,\
        default = 40)
    def _main(self):
        self_symbols = cast(dict[str, str],\
            self.symbols) # type: ignore
        self_ddos_delay = cast(float,\
            self.ddos_delay) # type: ignore
        self_ddos_max = cast(int,\
            self.ddos_max) # type: ignore
        self_net_delay = cast(float,\
            self.net_delay) # type: ignore
        self_net_max = cast(int,\
            self.net_max) # type: ignore
        if self_symbols is not None:
            for key, value in self_symbols.items():
                print(f"{key}/{value}")
        appio = src.inner.AppIO.create()
        try:
            # Get directories
            pydir = pathlib.Path(sys.argv[0]).resolve().parent
            secretdir = pydir.joinpath("secret")
            # Get API info
            apipath = secretdir.joinpath("cdp_api_key.json")
            api = src.inner.APIInfo(apipath)
            # Create crypto interface
            cry = src.inner.Cry(api)
            # Loop
            app = src.App(cry, appio,\
                self_ddos_delay,\
                self_ddos_max,\
                self_net_delay,\
                self_net_max,\
                {} if (self_symbols is None) else self_symbols)
            asyncio.run(loop(app))
            # Success!!!
            return 0
        except src.inner.CLIError as _e:
            e = _e
        finally:
            appio.destroy()
        # ERROR
        print(f"ERROR: {e.etype} {e}", file = sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(Cmd().execute(sys.argv))
# ------------------------------------------------------------------------->
import asyncio
import pathlib
import sys

import src

async def main_loop(app:src.App):
    looping = True
    error = None
    loop = asyncio.get_running_loop()
    update_params = src.AppUpdateParams()
    update_result = src.AppUpdateResult() # Trick the loop so an initial update will be triggered
    while looping:
        # Input
        _key = app.appio.get_ch()
        if _key != -1: update_params.input_add(_key)
        # Update
        if update_result is not None:
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

def main():
    if len(sys.argv) == 0: return 1
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
        asyncio.run(main_loop(src.App(cry, appio)))
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
    sys.exit(main())
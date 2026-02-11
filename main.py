import pathlib
import sys

import src

def main():
    try:
        if len(sys.argv) == 0: return 1
        # Get directories
        pydir = pathlib.Path(sys.argv[0]).resolve().parent
        secretdir = pydir.joinpath("secret")
        # Get API info
        apipath = secretdir.joinpath("cdp_api_key.json")
        api = src.APIInfo(apipath)
        # Create crypto interface
        cry = src.Cry(api)
        balance = cry.get_balance('USD')
        # order = cry.order_buy('BTC/USD', 5)
# ------------------------------------------------------------------------->
        
        print(f"USD Balance: {balance}")
    except src.CLIError as _e:
        print(f"ERROR: {_e}", file = sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
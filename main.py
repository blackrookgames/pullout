# ------------------------------------------------------------------------->
import pathlib
import sys

import src

def main():
    try:
        if len(sys.argv) == 0: return 1
        # What to do?
        whattodo = '0'
        if len(sys.argv) > 1:
            whattodo = sys.argv[1]
        # Get directories
        pydir = pathlib.Path(sys.argv[0]).resolve().parent
        secretdir = pydir.joinpath("secret")
        # Get API info
        apipath = secretdir.joinpath("cdp_api_key.json")
        api = src.APIInfo(apipath)
        # Create crypto interface
        cry = src.Cry(api)
        # Do what to do
        match whattodo:
            case '0':
                balance = cry.get_balance('USD')
                print(f"Balance: {balance} USD")
            case '1':
                amount = 5
                markets = cry.load_markets()
                order = cry.order_buy('BTC/USD', amount)
                print(f"Bought {amount} USD worth of BTC")
            case '2':
                amount = 5
                order = cry.order_sell('BTC/USD',\
                    cry.compute_from('BTC/USD', amount))
                print(f"Sold {amount} USD worth of BTC")
            case _:
                raise src.CLIError(f"Invalid code: {whattodo}")
    except src.CLIError as _e:
        print(f"ERROR: {_e}", file = sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
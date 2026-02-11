import ccxt
import json
import pathlib
import sys

def fetch_market_depth(exchange, symbol):
    try:
        # 2. Fetch the order book
        # 'limit=5' gets the top 5 best buy/sell prices
        orderbook = exchange.fetch_order_book(symbol, limit=5)
        
        bids = orderbook['bids'] # Buyers
        asks = orderbook['asks'] # Sellers

        print(f"\n--- {symbol} Market Depth ---")
        print("Asks (Sellers):")
        for ask in reversed(asks): # Reversed so higher prices are on top
            print(f"  Price: {ask[0]} | Amount: {ask[1]}")
            
        print(f"--- Spread: {asks[0][0] - bids[0][0]:.2f} ---")
        
        print("Bids (Buyers):")
        for bid in bids:
            print(f"  Price: {bid[0]} | Amount: {bid[1]}")

    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) == 0: return 1
    pydir = pathlib.Path(sys.argv[0]).resolve().parent
    tsdir = pydir.joinpath("secret")
    # 1. Load the JSON file
    apikeypath = tsdir.joinpath("cdp_api_key.json")
    with open(apikeypath, 'r') as f:
        key_data = json.load(f)
    # 2. Extract the specific fields
    # Coinbase JSON uses 'name' for the Key and 'privateKey' for the Secret
    exchange = ccxt.coinbase({ \
        'apiKey': key_data['name'], \
        'secret': key_data['privateKey'], \
        'enableRateLimit': True, })
    # Run it
    fetch_market_depth(exchange, 'BTC/USDT')
    # Success!!!
    return 0

if __name__ == "__main__":
    sys.exit(main())
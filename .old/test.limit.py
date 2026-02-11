import ccxt
import json

# Load your keys
with open('./secret/cdp_api_key.json', 'r') as f:
    key_data = json.load(f)

exchange = ccxt.coinbase({
    'apiKey': key_data['name'],
    'secret': key_data['privateKey'],
    'enableRateLimit': True,
})

symbol = 'BTC/USD'

try:
    # 1. Get the current price dynamically
    ticker = exchange.fetch_ticker(symbol)
    current_price = float(ticker['last']) #type: ignore
    
    # 2. Set the test price 5% BELOW the current price
    # This is close enough to pass the 'Far From Market' check,
    # but far enough that it won't fill immediately.
    test_price = current_price * 0.95 
    amount = 0.0001 

    print(f"Current BTC Price: ${current_price}")
    print(f"Placing Test Order at: ${test_price:.2f} (5% below market)")

    # 3. Place the order
    order = exchange.create_limit_buy_order(symbol, amount, test_price)
    
    print(f"Success! Order ID: {order['id']}")
    print("Go to your Coinbase dashboard to see it in 'Open Orders'.")

except Exception as e:
    print(f"Still hitting a snag: {e}")
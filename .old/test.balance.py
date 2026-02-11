import ccxt
import json

# 1. Load the JSON file
with open('./secret/cdp_api_key.json', 'r') as f:
    key_data = json.load(f)

# 2. Extract the specific fields
# Coinbase JSON uses 'name' for the Key and 'privateKey' for the Secret
exchange = ccxt.coinbase({
    'apiKey': key_data['name'],
    'secret': key_data['privateKey'],
    'enableRateLimit': True,
})

# 3. Test it out
try:
    balance = exchange.fetch_balance()
    print("Successfully connected using JSON file!")
    print(f"USD Balance: {balance.get('USD', {}).get('total', 0)}")
except Exception as e:
    print(f"Connection failed: {e}")
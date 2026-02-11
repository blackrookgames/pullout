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

# Assuming your 'exchange' object is already set up
accounts = exchange.fetch_accounts()

print(f"{'Currency':<10} | {'Available':<15} | {'Account ID'}")
print("-" * 50)

for acc in accounts:
    # Only show accounts that actually have money or are USD
    if float(acc['info'].get('available_balance', {}).get('value', 0)) > 0 or acc['code'] == 'USD':
        code = acc['code']
        balance = acc['info'].get('available_balance', {}).get('value', 0)
        account_id = acc['id']
        print(f"{code:<10} | {balance:<15} | {account_id}")
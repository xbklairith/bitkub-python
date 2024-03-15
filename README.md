# bitkub-python
A Python client for Bitkub API 

## ⚠️ Disclaimer: This is not an official Bitkub library. Use at your own risk. 
- This library is not guaranteed to be up-to-date with the latest Bitkub API.
- Before using the library, please check the [API documentation](https://github.com/bitkub/bitkub-official-api-docs) to be informed about the latest updated or possible bugs.


## Features
- Trading support
- General market data and account information
- Handling of authentication  
- Deposit and withdrawal of funds





## Getting Started

[Generate an API Key](https://www.bitkub.com/en/api-management) and assign permissions.

### Installation
```bash
pip install bitkub-python
```


### Usage
```python
from bitkub import Client
client = Client("apikey" , "apisecret")

orderbooks = client.fetch_depth(symbol='THB_ETH', limit=10)

# create order
order = client.create_order_buy(symbol='USDT_THB', amount=10, rate=30)

# cancel order
client.cancel_order(order_id=order['id'])

# fetch open orders
client.fetch_open_orders(symbol='BTC_THB')

```


## Buy me a coffee ☕
if you find this library useful, please consider buying me a coffee.
- [Buy me a coffee ☕](https://www.buymeacoffee.com/xbklairith)

Ref : 
- [bitkub-official-api-doc](https://github.com/bitkub/bitkub-official-api-docs)

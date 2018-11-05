from binance.client import Client
from config import api_key, api_secret
import binance_constants

"""
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
  ]
]
"""

# 0.000011645
symbol = 'BNBBTC'
quantity = '20'
period = 10
delta = .00000001
client = Client(api_key, api_secret)
info = client.get_symbol_info(symbol)
ADA = client.get_historical_klines(symbol=symbol, interval=binance_constants.KLINE_INTERVAL_1HOUR, start_str="1 day ago UTC")
holdings = 50.
moving_avg = 0
trade_placed = False
trade_type = False
epsilon = 0.0000001

for i in range(len(ADA)-1):
    ask_price = (float(ADA[i+1][2]) + float(ADA[i+1][3])) / 2
    last_price = (float(ADA[i][2]) + float(ADA[i][3])) / 2
    active_avg = (float(ADA[i+1][2]) + float(ADA[i+1][3]) +
                  float(ADA[i][2]) + float(ADA[i][3]))/4
    if not trade_placed:
        if ask_price + epsilon > active_avg and ask_price < last_price + epsilon:
            print("SELL")
            trade_placed = True
            trade_type = "short"
        elif ask_price < active_avg + epsilon and ask_price + epsilon > last_price:
            print("BUY")
            trade_placed = True
            trade_type = "long"
    elif trade_type == "short":
        if ask_price < active_avg + epsilon:
            print("Exit Short Trade")
            trade_placed = False
            trade_type = False
    elif trade_type == 'long':
        if ask_price > active_avg + epsilon:
            print("Exit Long Trade")
            trade_placed = False
            trade_type = False
    print("-"*50)
    print(f"Active Average: {active_avg}\naskPrice: {ask_price}\nlast_price: {last_price}")
    print("-"*50)

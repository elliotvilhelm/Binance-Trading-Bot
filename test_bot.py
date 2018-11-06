from binance.client import Client
from config import api_key, api_secret
import binance_constants
from trade import Trade

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
ADA = client.get_historical_klines(symbol=symbol, interval=binance_constants.KLINE_INTERVAL_1MINUTE, start_str="1 day ago UTC")

btc_holdings = 50.
bnb_holdings = 0.
moving_avg = 0
trade_placed = False
trade_type = False
epsilon = 0.0000001

sell_gamma = 1.0
buy_gamma = .99999
long_exit_gamma = 1.0
short_exit_gamma = 1.00
moving_avg_length = 100

trades = []
prices = []
for i in range(len(ADA)-1):
    ask_price = (float(ADA[i+1][2]) + float(ADA[i+1][3]) + float(ADA[i+1][4])) / 3
    last_price = (float(ADA[i][2]) + float(ADA[i][3]) + float(ADA[i][4])) / 3
    prices.append(ask_price)
    active_avg = sum(prices) / len(prices)
    if not trade_placed:
        if ask_price/active_avg > sell_gamma and ask_price/last_price < sell_gamma:
            if bnb_holdings > 0:
                print("SELL")
                trade_placed = True
                trade_type = "short"
                btc_holdings += 1
                bnb_holdings -= 1
                trades.append(Trade(ask_price, .002, trade_type))

        elif ask_price/active_avg < buy_gamma and ask_price/last_price > buy_gamma:
            if btc_holdings > 0:
                print("BUY")
                trade_placed = True
                trade_type = "long"
                btc_holdings -= 1
                bnb_holdings += 1
                trades.append(Trade(ask_price, .002, trade_type))

    elif trade_type == "short":
        if ask_price/active_avg < short_exit_gamma:
            print("Exit Short Trade")
            trade_placed = False
            trade_type = False
    elif trade_type == 'long':
        if ask_price/active_avg > long_exit_gamma:
            print("Exit Long Trade")
            trade_placed = False
            trade_type = False
    # print("-"*50)
    # print(f"Active Average: {active_avg}\naskPrice: {ask_price}\nlast_price: {last_price}")
    prices = prices[-moving_avg_length:]


sum_buy = 0
sum_sell = 0
initial_wallet = 50.
pocket = 50.
holdings = 0
for trade in trades:
    if trade.type == 'long':
        pocket -= trade.quantity * trade.price
        sum_buy += trade.quantity * trade.price
        holdings += trade.quantity
    else:
        holdings -= trade.quantity
        pocket += trade.quantity * trade.price
        sum_sell += trade.quantity * trade.price

ask_price = (float(ADA[-1][2]) + float(ADA[-1][3]) + float(ADA[-1][4])) / 3
post_assets = pocket + holdings * ask_price
profit = post_assets - initial_wallet
print("profit: ", profit)


from binance.enums import *
from utils import float_to_str
from math import ceil
import logging
logging.basicConfig(filename='output.log', level=logging.INFO)
from trade import Trade


class MovingAverage:
    def __init__(self, bot, trade_coin, backtest=False):
        self.bot = bot
        self.sell_gamma = 1.0
        self.buy_gamma = 1.0
        self.long_exit_gamma = 1.0
        self.short_exit_gamma = 1.0
        self.two_step_buy = 0
        self.two_step_sell = 0
        self.prices = []
        self.moving_avg_length = 100
        self.quantity = 10
        self.orders = 0
        self.trade_placed = False
        self.trade_type = False
        self.order = False
        self.trade_coin = trade_coin
        self.trades = []
        self.backtest = backtest

    def moving_avg(self, ask_price=None, last_price=None, base_coin_balance=0, trade_coin_balance=0):
        if not self.backtest:
            ticker = self.bot.client.get_ticker(symbol=self.trade_coin + self.bot.base_coin)
            ask_price = float(ticker['askPrice'])
            last_price = float(ticker['lastPrice'])
            trade_coin_balance = float(self.bot.client.get_asset_balance(asset=self.trade_coin)['free'])
            base_coin_balance = float(self.bot.client.get_asset_balance(asset=self.bot.base_coin)['free'])
            bid_price = float(ticker['bidPrice'])
            min_quantity = ceil(.001 / float(ticker['bidPrice']))
        else:
            # bid_price = (ask_price + last_price) / 2
            bid_price = ask_price
            min_quantity = ceil(.001 / bid_price)
        trade = None
        self.prices.append(ask_price)
        active_avg = sum(self.prices) / len(self.prices)

        # print(f"ask: {ask_price} last: {last_price}")
        # print("*"*50)
        # print("Trade Placed: ", self.trade_placed)
        # print(f"sell criteria:\n"
        #       f"ask_price/active_avg: {ask_price/active_avg} > 1.0?\n"
        #       f"ask_price/last_price: {ask_price/last_price} < 1.0?")
        # print("*"*50)
        # print(f"buy criteria:\n"
        #       f"ask_price/active_avg: {ask_price/active_avg} < 1.0?\n"
        #       f"ask_price/last_price: {ask_price/last_price} > 1.0?")
        # print("*"*50)
        if not self.trade_placed:
            # SELL
            if ask_price/active_avg > self.sell_gamma and ask_price/last_price < self.sell_gamma:
                logging.info(f"min quant sell: {min_quantity} coin: {self.trade_coin}")
                if trade_coin_balance > min_quantity:
                    if not self.backtest:
                        self.order = self.bot.client.create_order(
                            symbol=self.trade_coin + self.bot.base_coin,
                            side=SIDE_SELL,
                            type=ORDER_TYPE_LIMIT,
                            timeInForce=TIME_IN_FORCE_GTC,
                            quantity=min_quantity,
                            price=bid_price)
                    trade = Trade(bid_price, min_quantity, "short", self.trade_coin + self.bot.base_coin)
                    # print("sell -> bid price * min_quantity", bid_price * min_quantity)
                    base_coin_balance += bid_price * min_quantity
                    trade_coin_balance -= min_quantity
                    self.trades.append(trade)
                    if not self.backtest:
                        logging.info(f"SELL {self.trade_coin}  PRICE: {ticker['bidPrice']}  QUANTITY: {min_quantity}")
                    self.trade_placed = True
                    self.trade_type = 'short'
            # BUY
            elif ask_price/active_avg < self.buy_gamma and ask_price/last_price > self.buy_gamma:
                min_quantity = ceil(.001 / float(ask_price))
                self.two_step_buy += 1
                if base_coin_balance > min_quantity * ask_price and self.two_step_buy >= 2:
                    if not self.backtest:
                        self.order = self.bot.client.create_order(
                            symbol=self.trade_coin + self.bot.base_coin,
                            side=SIDE_BUY,
                            type=ORDER_TYPE_LIMIT,
                            timeInForce=TIME_IN_FORCE_GTC,
                            quantity=min_quantity,
                            price=ticker['askPrice'])
                    base_coin_balance -= bid_price * min_quantity
                    trade_coin_balance += min_quantity  # trade coin balance in BTC
                    trade = Trade(bid_price, min_quantity, "long", self.trade_coin + self.bot.base_coin)
                    # print("buy -> bid price * min_quantity", bid_price * min_quantity)
                    self.trades.append(trade)
                    if not self.backtest:
                        logging.info(f"BUY {self.trade_coin}  PRICE: {ticker['askPrice']}  QUANTITY: {min_quantity}")
                    self.two_step_buy = 0
                    self.trade_placed = True
                    self.trade_type = 'long'
        elif self.trade_type == "short":
            if ask_price/active_avg < self.short_exit_gamma:
                logging.info(f"Exit Trade {self.trade_coin}")
                # print("Exit Short Trade")
                if self.trade_placed:
                    try:
                        self.bot.client.cancel_order(symbol=self.trade_coin + self.bot.base_coin, orderId=self.order)
                        self.trade_placed = False
                        self.trade_type = False
                    except:
                        pass
                if self.backtest:
                    # pass
                    self.trade_placed = False
                    self.trade_type = False
        elif self.trade_type == 'long':
            if ask_price/active_avg > self.long_exit_gamma:
                # print("Exit Long Trade")
                logging.info(f"Exit Trade {self.trade_coin}")
                if self.trade_placed and not self.backtest:
                    try:
                        self.bot.client.cancel_order(symbol=self.trade_coin + self.bot.base_coin, orderId=self.order)
                        self.trade_placed = False
                        self.trade_type = False
                    except:
                        pass
                if self.backtest:
                    # pass
                    self.trade_placed = False
                    self.trade_type = False

        self.prices = self.prices[-self.moving_avg_length:]
        logging.info(f"Ticker: {self.trade_coin + self.bot.base_coin} Moving Average: {float_to_str(active_avg)}   Ask Price: {float_to_str(ask_price)}   Last Price: {float_to_str(last_price)}")
        return trade, base_coin_balance, trade_coin_balance


# holding 50.0 btc
# exchange rate .1 btc for 1 xrp
# btc: $5,000
# xrp: $200
# btc: 1
# xrp: 10
# BUY 1 xrp at .1
# btc: .9
# xrp: 1
# exchange rate .2 btc for 1 xrp

# 1 XRP -> .000088266 BTC
# amount of XRP in BTC = exchange * quantity







from binance.enums import *
from utils import float_to_str
from math import ceil
import logging
logging.basicConfig(filename='output.log', level=logging.INFO)


class MovingAverage:
    def __init__(self, bot, trade_coin):
        self.bot = bot
        self.sell_gamma = 1.0
        self.buy_gamma = 0.9999999
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

    def moving_avg(self):
        ticker = self.bot.client.get_ticker(symbol=self.trade_coin + self.bot.base_coin)
        ask_price = float(ticker['askPrice'])
        last_price = float(ticker['lastPrice'])
        self.prices.append(ask_price)
        active_avg = sum(self.prices) / len(self.prices)
        if not self.trade_placed:
            if ask_price/active_avg > self.sell_gamma and ask_price/last_price < self.sell_gamma:
                balance = float(self.bot.client.get_asset_balance(asset=self.trade_coin)['free'])
                min_quantity = ceil(.001 / float(ticker['bidPrice']))
                if balance > min_quantity * float(ticker['bidPrice']):
                    self.order = self.bot.client.create_test_order(
                        symbol=self.trade_coin + self.bot.base_coin,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=min_quantity,
                        price=ticker['bidPrice'])
                    logging.info(f"SELL {self.trade_coin}  PRICE: {ticker['bidPrice']}  QUANTITY: {min_quantity}")
                    self.trade_placed = True
                    self.trade_type = 'short'
            elif ask_price/active_avg < self.buy_gamma and ask_price/last_price > self.buy_gamma:
                balance = float(self.bot.client.get_asset_balance(asset=self.bot.base_coin)['free'])
                min_quantity = ceil(.001 / float(ask_price))
                self.two_step_buy += 1
                if balance > min_quantity * ask_price and self.two_step_buy >= 2:
                    self.order = self.bot.client.create_test_order(
                        symbol=self.trade_coin + self.bot.base_coin,
                        side=SIDE_BUY,
                        type=ORDER_TYPE_LIMIT,
                        timeInForce=TIME_IN_FORCE_GTC,
                        quantity=min_quantity,
                        price=ticker['askPrice'])
                    logging.info(f"BUY {self.trade_coin}  PRICE: {ticker['askPrice']}  QUANTITY: {min_quantity}")
                    self.two_step_buy = 0
                    self.trade_placed = True
                    self.trade_type = 'long'
        elif self.trade_type == "short":
            if ask_price/active_avg < self.short_exit_gamma:
                logging.info(f"Exit Trade {self.trade_coin}")
                if self.trade_placed:
                    try:
                        self.bot.client.cancel_order(symbol=self.trade_coin + self.bot.base_coin, orderId=self.order)
                    except:
                        pass
                self.trade_placed = False
                self.trade_type = False
        elif self.trade_type == 'long':
            if ask_price/active_avg > self.long_exit_gamma:
                logging.info(f"Exit Trade {self.trade_coin}")
                if self.trade_placed:
                    try:
                        self.bot.client.cancel_order(symbol=self.trade_coin + self.bot.base_coin, orderId=self.order)
                    except:
                        pass
                self.trade_placed = False
                self.trade_type = False

        self.prices = self.prices[-self.moving_avg_length:]
        logging.info(f"Ticker: {self.trade_coin + self.bot.base_coin} Moving Average: {float_to_str(active_avg)}   Ask Price: {float_to_str(ask_price)}   Last Price: {float_to_str(last_price)}")

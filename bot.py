from binance.client import Client
from config import api_key, api_secret
from strategy import MovingAverage
import binance_constants
from trade import Trade

class Bot:
    def __init__(self, base_coin='BTC', symbols=['XRP', 'XLM', 'ADA', 'BAT'], backtest=True):
        self.client = Client(api_key, api_secret)
        self.symbols = symbols
        self.backtest = backtest

        """ base coin """
        self.base_coin = base_coin
        self.base_coin_balance = self.client.get_asset_balance(asset=self.base_coin)['free']

        """ trade coins """
        self.trade_coin_tickers = {}
        self.update_tickers()
        self.period = 10

        """ trades """
        self.active_trade_limit = 1
        self.active_trades = {}
        self.trade_id = 0

        self.moving_avgs = []
        symbols = ['XRP']
        for s in symbols:
            self.moving_avgs.append(MovingAverage(self, s, backtest=self.backtest))

    def tick(self):
        for m in self.moving_avgs:
            m.moving_avg()

    def run_backtest(self):
        base_coin_balance = 1.
        trade_coin_balance = 0.
        data = self.client.get_historical_klines(symbol='XRPBTC', interval=binance_constants.KLINE_INTERVAL_1MINUTE, start_str="10 days ago UTC")
        trades = []
        print("data size: ", len(data))
        for i in range(len(data)-2):
            ask_price = (float(data[i+1][2]) + float(data[i+1][3]) + float(data[i+1][4])) / 3
            last_price = (float(data[i][2]) + float(data[i][3]) + float(data[i][4])) / 3
            trade, base_coin_balance, trade_coin_balance = self.moving_avgs[0].moving_avg(ask_price, last_price, base_coin_balance, trade_coin_balance)
            if trade:
                pass
                # print(f"Trade\nType:  {trade.trade_type}   Quantity: {trade.quantity}   Exchange: {trade.exchange}")
            if trade is not None:
                trades.append(trade)
        ask_price = (float(data[-1][2]) + float(data[-1][3]) + float(data[-1][4])) / 3
        total = base_coin_balance + ask_price * trade_coin_balance
        print("Total holdings: ", total, "BTC")

    def update_tickers(self):
        for s in self.symbols:
            self.trade_coin_tickers.update({s: self.client.get_symbol_ticker(symbol=(s + self.base_coin))})

    def update_trades(self):
        pass



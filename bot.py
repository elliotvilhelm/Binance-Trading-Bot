from binance.client import Client
from config import api_key, api_secret
from strategy import MovingAverage

class Bot:
    def __init__(self, base_coin='BTC', symbols=['XRP', 'BCC', 'BAT']):
        self.client = Client(api_key, api_secret)
        self.symbols = symbols

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

        self.m1 = MovingAverage(self, 'XRP')
        self.m2 = MovingAverage(self, 'BCC')
        self.m3 = MovingAverage(self, 'BAT')

    def tick(self):
        # self.update_tickers()
        self.m1.moving_avg()
        self.m2.moving_avg()
        self.m3.moving_avg()

    def update_tickers(self):
        for s in self.symbols:
            self.trade_coin_tickers.update({s: self.client.get_symbol_ticker(symbol=(s + self.base_coin))})

    def update_trades(self):
        pass



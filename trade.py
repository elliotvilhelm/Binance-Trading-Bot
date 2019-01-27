class Trade:
    def __init__(self, price, quantity, trade_type, exchange):
        self.open = False
        self.quantity = quantity
        self.price = price
        self.trade_type = trade_type
        self.exchange = exchange

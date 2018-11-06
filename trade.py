class Trade:
    def __init__(self, price, quantity, trade_type):
        self.open = False
        self.quantity = quantity
        self.price = price
        self.type = trade_type

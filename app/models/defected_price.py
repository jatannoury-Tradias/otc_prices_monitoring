class DefectedPrice:
    def __init__(self, instrument=None, quantity=None, difference_with_old=None, difference_with_new=None, price_timestamp=None):
        self.instrument = instrument
        self.quantity = quantity
        self.difference_with_old = difference_with_old
        self.difference_with_new = difference_with_new
        self.price_timestamp = price_timestamp


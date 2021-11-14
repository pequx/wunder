class Order(object):
    __slots__ = ["timestamp", "side", "price", "quantity"]

    def __init__(self, timestamp, side, price, quantity):
        self.timestamp = timestamp
        self.side = side
        self.price = price
        self.quantity = quantity

    def get(self, slot):
        return self.__getattribute__(slot)

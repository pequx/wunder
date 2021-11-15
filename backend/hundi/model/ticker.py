from hundi.config.ticker import TICKER_SLOTS


class TickerFutures(object):
    __slots__ = TICKER_SLOTS['FUTURES']

    def __init__(self, timestamp, bid, ask, bid_size, ask_size, volume):
        self.timestamp = timestamp
        self.bid = bid
        self.ask = ask
        self.bid_size = bid_size
        self.ask_size = ask_size
        self.volume = volume

    def get(self, slot):
        return self.__getattribute__(slot)


class TickerSpot(object):
    __slots__ = TICKER_SLOTS['SPOT']

    def __init__(self, timestamp, open, high, low, close, volume=None):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def get(self, slot):
        return self.__getattribute__(slot)


class TickerFTX(object):
    __slots__ = TICKER_SLOTS['FTX']

    def __init__(self, timestamp, bid, ask, bid_size, ask_size):
        self.timestamp = timestamp
        self.bid = bid
        self.ask = ask
        self.bid_size = bid_size
        self.ask_size = ask_size

    def get(self, slot):
        return self.__getattribute__(slot)

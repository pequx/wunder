import collections

from hundi.config.candle import (CANDLE_PERIODS, CANDLE_SLOTS)

CandleTuple = collections.namedtuple(
    "Candle", "timestamp period open high low close volume"
)


class CandlePeriod(object):
    def __init__(self, period):
        if isinstance(period, str):
            self.seconds = CANDLE_PERIODS.get(period)
            if not self.seconds:
                raise ValueError(
                    "CandlePeriod string not recognized: {}".format(period)
                )
            self.string = period
        elif isinstance(period, int):
            self.seconds = period
            if period not in CANDLE_PERIODS.values():
                raise ValueError(
                    "CandlePeriod not defined: {}s".format(period)
                )
            self.string = [
                k for k, v in CANDLE_PERIODS.items() if v == period
            ][0]
        else:
            raise ValueError("Unknown type of argument for CandlePeriod")

    def __int__(self):
        return self.seconds

    def __str__(self):
        return self.string

    def candle_start(self, timestamp):
        """ Returns timestamp of beginning of candle """
        return int(timestamp / self.seconds) * self.seconds

    def next_candle_start(self, timestamp):
        """ Returns timestamp of beginning of next candle """
        return self.candle_start(timestamp + self.seconds)

    def candle_end(self, timestamp):
        """ Returns timestamp of end of candle """
        return self.next_candle_start(timestamp) - 1


class Candle(object):
    __slots__ = CANDLE_SLOTS

    def __init__(
        self,
        timestamp,
        period: CandlePeriod,
        open,
        high,
        low,
        close,
        volume
    ):
        self.timestamp = timestamp
        self.period = period
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def get(self, slot):
        return self.__getattribute__(slot)

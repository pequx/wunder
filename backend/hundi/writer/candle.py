import datetime
import logging
from abc import ABC, abstractmethod

from hundi.lib.kairosdb import candle as kairosdb
from hundi.lib.helper import get_metric_name
from hundi.config.message import (
    CANDLE_WRITTEN,
    CANDLES_BUFFER_SIZE,
    CANDLES_WRITTEN_COUNT
)
from hundi.config.candle import CANDLE_BUFFER_SIZE
from hundi.model.candle import Candle

logger = logging.getLogger(__name__)


class CandleWriter(ABC):
    @abstractmethod
    def write(self, exchange, currency, asset, candle: Candle, timestamp):
        """ Save a single candle """
        raise NotImplementedError


class TradeOutOfOrderException(Exception):
    pass


class DictionaryCandleWriter(CandleWriter):
    def __init__(self, output):
        self.output = output

    def write(self, key, candle: Candle):
        self.output.append(
            {
                "pair": key,
                "timestamp": datetime.datetime.fromtimestamp(candle.timestamp),
                "open": candle.open,
                "high": candle.high,
                "low": candle.low,
                "close": candle.close,
                "volume": candle.volume,
            }
        )
        logger.debug(
            CANDLE_WRITTEN.format(
                key,
                candle.period.string,
                datetime.datetime.fromtimestamp(candle.timestamp),
                candle.open,
                candle.high,
                candle.low,
                candle.close,
                candle.volume,
            )
        )


class KairosDBCandleWriter(CandleWriter):
    def __init__(self, exchange="default"):
        self.exchange = exchange
        self.buffer = []
        self.count = 0
        self.type = "crypto"
        self.source = "candle_writer.py"
        pass

    def write(self, key, candle: Candle):
        tags = {"source": self.source}
        path = get_metric_name(
            type=self.type,
            exchange=self.exchange,
            key=key,
            period=candle.period.string
        )

        if len(self.buffer) > CANDLE_BUFFER_SIZE:
            kairosdb.put_candles(path, self.buffer, tags)
            logger.debug(CANDLES_WRITTEN_COUNT.format(self.count))
            self.buffer = []

        self.buffer.append(candle)
        self.count += 1
        logger.debug(CANDLES_BUFFER_SIZE.format(len(self.buffer)))

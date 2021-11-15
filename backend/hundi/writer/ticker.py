import datetime
import logging
from abc import ABC, abstractmethod

from hundi.lib import helper
from hundi.lib.kairosdb import ticker as kairosdb
from hundi.config.message import (TICKERS_BUFFER_SIZE, TICKERS_WRITTEN_COUNT, UNKNOWN_MARKET_TYPE)
from hundi.config.market import MARKET_FTX_NAME
from hundi.model.ticker import TickerFutures, TickerSpot

logger = logging.getLogger(__name__)


class TickerWriter(ABC):
    @abstractmethod
    def write(self, pair: str, timestamp: str, ticker: TickerFutures or TickerSpot,
              market_type: str = "futures", marek="fja"):
        raise NotImplementedError


class DictionaryTickerWriter(TickerWriter):
    def __init__(self, output):
        self.output = output

    def get_timestamp(ticker):
        return datetime.datetime.fromtimestamp(ticker.timestamp)

    def write(self, pair, ticker, market_type="futures"):
        if market_type == "futures":
            self.output.append(
                {
                    "pair": pair,
                    "timestamp": self.get_timestamp(ticker),
                    "bid": ticker.bid,
                    "ask": ticker.ask,
                    "bid_size": ticker.bid_size,
                    "ask_size": ticker.ask_size,
                    "volume": ticker.volume,
                }
            )
        elif market_type == "spot":
            self.output.append(
                {
                    "pair": pair,
                    "timestamp": self.get_timestamp(ticker),
                    "open": ticker.bid,
                    "high": ticker.high,
                    "low": ticker.low,
                    "close": ticker.close,
                    "volume": ticker.volume,
                }
            )
        else:
            logger.error(UNKNOWN_MARKET_TYPE)


class KairosDBTickerWriter(TickerWriter):
    def __init__(self, exchange="default", type="crypto", market_type="spot"):
        self.buffer = []
        self.count = 0
        self.exchange = exchange
        self.type = type
        self.market_type = market_type
        # self.pair = pair
        self.source = "ticker_writer.py"
        pass

    def write(self, pair, ticker, interval=0):
        tags = {"source": self.source}

        path = helper.get_metric_name(
            type=self.type,
            exchange=self.exchange,
            key=pair,
            period=(interval if interval > 0 else None),
            variant=("ticker" if interval == 0 else None),
        )
        self.buffer.append(ticker)
        self.count += 1

        if len(self.buffer) > TICKERS_BUFFER_SIZE:
            market_type = (
                "futures"
                if self.exchange == MARKET_FTX_NAME["SPOT"]
                else self.market_type
            )
            kairosdb.put_tickers(market_type, path, self.buffer, tags)
            logger.info(TICKERS_WRITTEN_COUNT.format(self.count))
            self.buffer = []

        logger.debug(TICKERS_BUFFER_SIZE.format(len(self.buffer)))

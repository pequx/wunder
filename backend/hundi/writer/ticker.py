import datetime
import logging

from abc import ABC, abstractmethod
from queue import Queue

from lib import helper
from lib.kairosdb.ticker import TickerKairosDbLib
from hundi.config.message import (TICKERS_WRITTEN_COUNT, UNKNOWN_MARKET_TYPE)
from hundi.config.ticker import TICKERS_BUFFER_SIZE
from hundi.config.market import MARKET_FTX_NAME
from model.ticker import TickerFutures, TickerSpot
from lib import helper
from hundi.config.settings import ENVIRONMENT

logger = logging.getLogger(__name__)


class TickerWriter(ABC):
    @abstractmethod
    def write(self, pair: str, timestamp: str, ticker: TickerFutures or TickerSpot,
              market_type: str = "futures", marek="fja"):
        raise NotImplementedError


# class DictionaryTickerWriter(TickerWriter):
#     def __init__(self, output):
#         self.output = output

#     def get_timestamp(ticker):
#         return datetime.datetime.fromtimestamp(ticker.timestamp)

#     def write(self, pair, ticker, market_type="futures"):
#         if market_type == "futures":
#             self.output.append(
#                 {
#                     "pair": pair,
#                     "timestamp": self.get_timestamp(ticker),
#                     "bid": ticker.bid,
#                     "ask": ticker.ask,
#                     "bid_size": ticker.bid_size,
#                     "ask_size": ticker.ask_size,
#                     "volume": ticker.volume,
#                 }
#             )
#         elif market_type == "spot":
#             self.output.append(
#                 {
#                     "pair": pair,
#                     "timestamp": self.get_timestamp(ticker),
#                     "open": ticker.bid,
#                     "high": ticker.high,
#                     "low": ticker.low,
#                     "close": ticker.close,
#                     "volume": ticker.volume,
#                 }
#             )
#         else:
#             logger.error(UNKNOWN_MARKET_TYPE)


class KairosDBTickerWriter(TickerWriter):
    def __init__(self, db: TickerKairosDbLib) -> None:
        self.queue = Queue(maxsize=TICKERS_BUFFER_SIZE)
        self.count = {
            "total": 0,
            "queue": 0
        }
        self.source = "{}.hundi.writer.ticker".format(ENVIRONMENT)
        self.db = db

    def write(self, path: str, ticker: TickerSpot or TickerFutures) -> bool:
        try:
            self.queue.put(ticker)
            self.count["queue"] = + 1
            self.queue.join()

            if self.count["queue"] >= TICKERS_BUFFER_SIZE:
                if self.db.put_tickers(path, tickers=self.queue.get(), tags={"source": self.source}) is False:
                    raise Exception("Write exception.")
                self.count["total"] += self.count["total"] + self.count["queue"]
                logger.info(TICKERS_WRITTEN_COUNT.format(self.count["total"]))
                self.queue.task_done()
                self.count["queue"] = 0
            logger.debug(TICKERS_BUFFER_SIZE.format(self.count["queue"]))

            return True
        except Exception as e:
            logger.exception(e)
            return False

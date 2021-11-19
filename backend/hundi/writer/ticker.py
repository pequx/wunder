import logging

from abc import ABC, abstractmethod
from queue import Queue

from lib import helper
from lib.kairosdb.ticker import TickerKairosDbLib
from hundi.config.message import (TICKERS_WRITTEN_COUNT)
from hundi.config.ticker import TICKERS_BUFFER_SIZE
from model.ticker import TickerFutures, TickerSpot
from hundi.config.settings import ENVIRONMENT

logger = logging.getLogger(__name__)


class KairosDBTickerWriter(ABC):
    def __init__(self, db: TickerKairosDbLib) -> None:
        self.queue = Queue(maxsize=TICKERS_BUFFER_SIZE)
        self.count = {
            "total": 0,
            "queue": 0
        }
        self.source = "{}.hundi.writer.ticker".format(ENVIRONMENT)
        self.db = db

    @abstractmethod
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

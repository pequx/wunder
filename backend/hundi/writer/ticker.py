import logging
import time

from queue import Queue
from threading import Thread
from typing import List

from hundi.lib.kairosdb.ticker import TickerKairosDbLib
from hundi.config.ticker import TICKERS_BUFFER_SIZE
from hundi.model.ticker import TickerFutures, TickerSpot
from hundi.config.settings import ENVIRONMENT
from hundi.lib import helper

logger = logging.getLogger(__name__)


class KairosDBTickerWriter(object):
    def __init__(self, paths: object) -> None:
        self._queue = Queue(maxsize=1000)
        self._buffer = {}
        self.count = 0
        self._thread = Thread(target=self.worker, name=__name__, daemon=True)
        self.lock = True
        self.db = {}
        self.paths = paths
        for name in self.paths:
            path = self.paths[name]
            self.db[name] = TickerKairosDbLib(path, {"source": "{}.{}".format(ENVIRONMENT, __name__)})
            self._buffer[name] = []

    @property
    def is_alive(self) -> bool:
        return self._thread.is_alive

    def start(self) -> None:
        try:
            for name in self.db:
                self.db[name].start()

                if self.db[name].lock:
                    raise Exception("Db lock present.")
            self._thread.start()
            self.lock = False
            logger.info("Started thread {} for {}".format(__name__, self.paths))
        except Exception as e:
            logger.exception(e)
            self.lock = True

    def stop(self) -> None:
        try:
            logger.info("Stopping thread {} for {} and queue with unfinished tasks: {}".format(
                __name__, self.paths, self._queue.unfinished_tasks))

            if self.count > 0:
                self._queue.join()

            for name in self.db:
                if self.db[name].is_alive:
                    self.db[name].stop()
                self.count = self._queue.unfinished_tasks

                if not self.db[name].lock:
                    raise Exception("Db lock not present.")
            self.lock = True
            self.db = {}
            if self.is_alive:
                self._thread.join(1)
        except Exception as e:
            logger.exception(e)
            self.lock = True

    def worker(self) -> None:
        logger.info("Starting worker for {}".format(self.paths))

        try:
            while True:
                if not self.lock:
                    start = time.time()
                    entry = self._queue.get()
                    name = entry.get('name')
                    buffer = entry.get('buffer')
                    size = len(buffer)

                    self._write(name, buffer)
                    self.count -= size

                    end = time.time()
                    duration = end - start
                    logger.debug("Proccessed {} tickers in {:.3f}s, {:.1f} entries/s".format(size, duration, size / duration))
                    self._queue.task_done()
        except Exception as e:
            logger.exception(e)
            self.stop()

    def put(self, name: str, ticker: TickerSpot or TickerFutures):
        try:
            if not self.lock:
                self._buffer[name].append(ticker)

                if len(self._buffer[name]) == 5:
                    self._queue.put_nowait({"name": name, "buffer": self._buffer[name]})
                    self.count += len(self._buffer[name])
                    self._buffer[name] = []

                logger.debug("Putted ticker to writer queue {}".format(ticker.timestamp))
        except Exception as e:
            logger.exception(e)
            self.stop()

    def _write(self, name: str, buffer: List[TickerSpot or TickerFutures]) -> None:
        try:
            if not self.lock:
                if self.db[name].lock:
                    raise Exception('Db lock present')

                self.db[name].put(buffer)
                logger.debug("Putted writter buffer to db {}".format(buffer))
        except Exception as e:
            logger.exception(e)
            self.stop()

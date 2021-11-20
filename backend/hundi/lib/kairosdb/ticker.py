import logging
import json
import time
import requests

from queue import Queue
from threading import Thread
from typing import List

from hundi.config.settings import KAIROSDB_TTL, KAIROSDB_URL, KAIROSDB_API_DATAPOINTS, ENVIRONMENT
from hundi.config.ticker import (
    TICKER_COLUMN_MAPPING,
    TICKER_DATAFRAME_TIME_UNIT,
    TICKER_START_RELATIVE,
    TICKER_END_RELATIVE,
    TICKER_DEFAULT_COLUMNS,
    TICKER_CACHE_TIME,
    TICKER_AGGREGATORS
)
from hundi.lib.kairosdb import query
from hundi.lib import helper
from hundi.model.ticker import TickerFutures, TickerSpot

logger = logging.getLogger(__name__)


class TickerKairosDbLib(object):
    def __init__(self, path: object, tags: object, ttl: int = KAIROSDB_TTL) -> None:
        self.path = helper.format_path(path)
        self.tags = tags
        self.mapping = TICKER_COLUMN_MAPPING[path['market_type']]
        self.count = 0
        self.ttl = ttl
        self._queue = Queue(maxsize=1000)
        self._thread = Thread(target=self.worker, name=self.path, daemon=True)
        self.lock = True

    @property
    def is_alive(self) -> bool:
        return self._thread.is_alive

    def start(self) -> None:
        try:
            self._thread.start()
            self.lock = False
            logger.info("Started thread {} for {}".format(__name__, self.path))
        except Exception as e:
            logger.exception(e)
            self.lock = True

    def stop(self) -> None:
        try:
            logger.info("Stopping thread {} for {} and queue with unfinished tasks: {}".format(
                __name__, self.path, self._queue.unfinished_tasks))
            if self.count > 0:
                self._queue.join()
                self.count = self._queue.unfinished_tasks

            self.lock = True
            if self.is_alive:
                self._thread.join(1)
        except Exception as e:
            logger.exception(e)

    def worker(self) -> None:
        logger.info("Starting worker for {}".format(self.path))

        try:
            while True:
                if not self.lock:
                    entries = self._queue.get()
                    self._request(entries)
                    self.count -= len(entries)
                    self._queue.task_done()
        except Exception as e:
            logger.exception(e)
            self.stop()

    def put(self, buffer: List[TickerSpot or TickerFutures]) -> None:
        try:
            if not self.lock:
                entries = []
                for column in self.mapping:
                    datapoints = []

                    for ticker in buffer:
                        timestamp = ticker.timestamp * 1000
                        value = ticker.get(column)
                        datapoints.append([timestamp, float(value)])

                    entries.append({
                        "name": self.path,
                        "datapoints": datapoints,
                        "tags": {
                            "source": self.tags['source'],
                            "column": self.mapping[column]
                        },
                        "ttl": self.ttl
                    })

                self.count += len(entries)

                logger.debug("Putting entries to queue {}".format(entries))
                self._queue.put_nowait(entries)

                logger.debug("Total datapoints count: {}".format(self.count))
        except Exception as e:
            logger.exception(e)
            self.stop()

    def _request(self, entries: List[object]):
        response = None

        try:
            if not self.lock:
                size = len(entries)

                if size < 1:
                    raise Exception("Invalid datapoints size.")

                start = time.time()
                url = KAIROSDB_URL if ENVIRONMENT != "development" else "http://host.docker.internal:8080"
                response = requests.post(url + KAIROSDB_API_DATAPOINTS, json.dumps(entries))
                logger.debug("Recived post response: {} : {}".format(response, entries))
                end = time.time()

                duration = end - start
                logger.info("Written {} entriess in {:.3f}s, {:.1f} entry/s".format(size, duration, size / duration))

                if response.status_code != 204:
                    raise Exception("Response error: {}".format(response))
        except Exception as e:
            logger.exception(e)
            self.stop()
    # def get_tickers_as_dataframe(
    #     type: str,
    #     exchange: str,
    #     market_type: str,
    #     metric_name: str,
    #     time_unit: str = TICKER_DATAFRAME_TIME_UNIT,
    #     start_relative: int = TICKER_START_RELATIVE,
    #     end_relative: int = TICKER_END_RELATIVE,
    #     last: bool = False,
    # ):
    #     try:
    #         tickers = query.query_as_dataframe(
    #             metric_name=helper.get_metric_name(
    #                 type=type,
    #                 exchange=exchange,
    #                 key=metric_name,
    #                 # period=(interval if interval > 0 else None),
    #                 # variant=("ticker" if interval == 0 else None),
    #                 variant="ticker",
    #             ),
    #             columns=TICKER_DEFAULT_COLUMNS[market_type.upper()],
    #             time_unit=time_unit,
    #             start_relative=start_relative,
    #             end_relative=end_relative,
    #             cache_time=TICKER_CACHE_TIME,
    #             aggregators=(
    #                 TICKER_AGGREGATORS["LAST"]
    #                 if last is True
    #                 else TICKER_AGGREGATORS["AVG"][time_unit.upper()]
    #             ),
    #         )
    #     except Exception as e:
    #         logger.warning("ticker exception {}".format(e))
    #     finally:
    #         logger.debug("tickers {}".format(tickers))
    #         return tickers

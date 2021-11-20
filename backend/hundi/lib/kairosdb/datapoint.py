import time
import requests
import logging
import json

from queue import Queue
from threading import Thread

from hundi.config.settings import (
    KAIROSDB_URL, KAIROSDB_API_DATAPOINTS, KAIROSDB_TTL
)

from hundi.config.message import (
    KARIOSDB_DATAPOINTS_PUT,
    KAIROSDB_ERROR_RESPONSE_STATUS
)

logger = logging.getLogger(__name__)


class DatapointKairosDbLib(object):
    def __init__(self, path: str, ttl: int = KAIROSDB_TTL) -> None:
        self.metric_name = path
        self.ttl = ttl
        self._queue = Queue(maxsize=1000)
        self._thread = Thread(target=self.worker, daemon=True, name=__name__)
        self.count = 0
        self.lock = True

    def start(self) -> None:
        try:
            self._thread.start()
            self.lock = False
            logger.info("Started thread {}".format(__name__))
        except Exception as e:
            logger.exception(e)
            self.lock = True

    def stop(self) -> None:
        try:
            logger.info("Stopped thread {} and queue with unfinished tasks: {}".format(
                __name__, self._queue.unfinished_tasks))
            self.lock = True
            self._queue.join()
            self._thread.join()
        except Exception as e:
            logger.exception(e)
            self.lock = True

    def worker(self) -> None:
        logger.info("Starting worker")

        try:
            while True:
                if not self.lock:
                    entry = self._queue.get()
                    datapoints = entry.get('datapoints')
                    size = len(datapoints)

                    if size < 1:
                        raise Exception("Invalid datapoints size.")

                    start = time.time()
                    self._post(entry)
                    end = time.time()

                    duration = end - start
                    logger.debug(
                        KARIOSDB_DATAPOINTS_PUT.format(
                            size,
                            entry['tags'],
                            duration,
                            size / duration))
                    self._queue.task_done()
        except Exception as e:
            logger.exception(e)
            self.stop()

    def put(self, datapoints, tags) -> None:
        try:
            if not self.lock:
                if len(datapoints) < 1:
                    raise Exception("No datapoints.")
                elif len(tags) < 1:
                    raise Exception("Tags missing.")

                entry = {
                    "name": self.metric_name,
                    "datapoints": datapoints,
                    "tags": tags,
                    "ttl": self.ttl,
                }
                logger.debug("Putting entry to the queue: {}".format(entry))

                self._queue.put(entry)
                self.count += 1
        except Exception as e:
            logger.exception(e)
            self.stop()

    def _post(self, entry):
        response = None

        try:
            response = requests.post(KAIROSDB_URL + KAIROSDB_API_DATAPOINTS, json.dumps([entry]))
            logger.debug("Recived post response: {}".format(response))

            if response.status_code != 204:
                raise Exception("Response error: {}".format(response))

            self.count -= 1
        except Exception as e:
            logger.exception(e)
            self.stop()

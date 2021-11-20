import asyncio
import logging

from threading import Thread

logger = logging.getLogger(__name__)


class AsyncioQueueLib(object):
    def __init__(self):
        self._queue = None
        self._thread = None
        self.count = {}
        self.lock = True

    def start(self) -> None:
        try:
            if self.lock:
                self._queue = asyncio.Queue()
                self._thread = Thread(target=self.worker, daemon=True, name=__name__)
                self.lock = False
        except Exception as e:
            logger.exception(e)
        finally:
            logger.info("Started thread for {}".format(__name__))

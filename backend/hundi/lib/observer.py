import logging
import re
import subprocess
import time

from threading import Thread
from queue import Queue

from hundi.config.settings import LOG_PATH, LOG_QUEUE_MAX_SIZE, LOG_UPDATE_INTERVAL, LOG_MAX_LINES
from hundi.config.message import THREAD_RUN_EXCEPTION, THREAD_LOOP_EXCEPTION

logger = logging.getLogger(__name__)


class Observer(Thread):
    def __init__(self, log_level: int, filter: str):
        self.log_level = log_level if log_level else logging.INFO
        self.queue = Queue(maxsize=LOG_QUEUE_MAX_SIZE)
        self.filter = filter

    def run_forever(self):
        try:
            sp = subprocess.Popen(["tail", "-n", str(LOG_MAX_LINES), "-f", LOG_PATH], stdout=subprocess.PIPE)
            while True:
                try:
                    line = sp.stdout.readline()
                    if self.filter:
                        logger.debug(self.filter)
                        result: re.Match = re.search(self.filter, line.decode('utf-8'))
                        # print(result)
                        # if len(result.match()) < 1:
                        if not result:
                            line = None
                    if line:
                        self.queue.put(line)
                        self.queue.join()
                    time.sleep(LOG_UPDATE_INTERVAL)
                except Exception as e:
                    logger.exception(THREAD_LOOP_EXCEPTION.format(e))
        except Exception as e:
            logger.exception(THREAD_RUN_EXCEPTION.format(e))

    @ property
    def status(self):
        try:
            return self._t._running
        except Exception as e:
            return False

    def start(self):
        self._t = Thread(target=self.run_forever)
        self._t.daemon = True
        self._t._running = True
        self._t.start()

    def stop(self):
        self._t._running = False
        self._t.join()

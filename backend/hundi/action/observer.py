import logging
import time

from lib.observer import Observer
from config.message import (
    INFO_KEYBOARD_INTERRUPT,
    ACTION_EXCEPTION,
    ACTION_STOP_EXCEPTION
)

logger = logging.getLogger(__name__)


def observe(log_level: int):
    observer = Observer(log_level)

    try:
        observer.start()
        try:
            while True:
                if observer.queue.empty is False:
                    print(observer.queue.get_nowait())
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info(INFO_KEYBOARD_INTERRUPT)
            pass

    except Exception as e:
        logger.exception(ACTION_EXCEPTION.format(e))
        try:
            observer.stop()
        except Exception as e:
            logger.exception(ACTION_STOP_EXCEPTION.format(e))

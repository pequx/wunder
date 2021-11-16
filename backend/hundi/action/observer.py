import logging
import click

from lib.observer import Observer
from config.message import (
    INFO_KEYBOARD_INTERRUPT,
    ACTION_LOOP_EXCEPTION,
    ACTION_STOP_EXCEPTION,
    ACTION_RUN_EXCEPTION
)

logger = logging.getLogger(__name__)


def observe(log_level: int, cli: click):
    observer = Observer(log_level)

    try:
        observer.start()
        while True:
            try:
                line = observer.queue.get()
                if not line:
                    break
                else:
                    observer.queue.task_done()
                    cli.echo(line)
            except Exception as e:
                logger.exception(ACTION_LOOP_EXCEPTION.format(e))
    except Exception as e:
        logger.exception(ACTION_RUN_EXCEPTION.format(e))
        try:
            observer.stop()
        except Exception as e:
            logger.exception(ACTION_STOP_EXCEPTION.format(e))
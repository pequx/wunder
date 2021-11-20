import logging
import json
from types import FunctionType
from typing import Any
import websocket

from threading import Thread
from hundi.action.crypto.ftx.ticker import TickerFtxCryptoAction

from hundi.writer.ticker import KairosDBTickerWriter


logger = logging.getLogger(__name__)


class WebSocketExecutorLib(object):
    def __init__(self, action: TickerFtxCryptoAction):
        self.start = action.start
        self._thread = Thread(target=self.start, name=__name__)
        self._ws = websocket.WebSocketApp(
            action.url,
            action.header,
            action.on_open,
            action.on_message,
            self.on_error,
            self.on_close
        )
        self.lock = action.lock
        self.stop = action.stop

    def on_error(self, ws: websocket.WebSocket, error: Any) -> None:
        if error.__doc__ == "Program interrupted by user.":
            logger.info(error.__doc__)
        else:
            logger.error("Websocket error".format(repr(error)))

        self.stop()

    def on_close(self, ws: websocket.WebSocket, status_code, message) -> None:
        try:
            self.stop()
            logger.info("Closing websocket {} {}".format(status_code, message))
            # if self._thread.is_alive:
            #     raise Exception("Thread not terminated")
        except Exception as e:
            logger.exception(e)

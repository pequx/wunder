import base64
import hashlib
import hmac
import json
import logging
import os
import time
from multiprocessing.dummy import Process as Thread

import websocket

from hundi.config.message import (
    WEBSCOKED_STARTED,
    WEBSOCKET_CLOSED,
    WEBSOCKET_ERROR,
    WEBSOCKET_EXCEPTION_ON_CLOSE,
    WEBSOCKET_STOPPED,
)
from hundi.config.market import MARKET_KRAKEN_WEBSOCKET_URL

logger = logging.getLogger(__name__)


class WebsocketAuth(object):
    def __init__(self, type="spot"):
        self._ws = websocket.WebSocketApp(
            MARKET_KRAKEN_WEBSOCKET_URL[type.upper()],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.token = ""

    def on_message(self, message):
        message = json.loads(message)
        logger.info(message)

    def get_token(self):
        api_nonce = bytes(str(int(time.time() * 1000)), "utf-8")
        api_secret = bytes(base64.b64decode(os.environ.get("MARKET_FTX_API_SECRET")))
        api_key = base64.b64decode(os.environ.get("MARKET_FTX_API_KEY"))
        sign = base64.encode(
            hmac.new(
                base64.b64decode(os.environ.get("MARKET_FTX_API_KEY")),
                hashlib.sha256(api_nonce + api_secret).digest(),
                hashlib.sha256,
            ).digest()
        )
        message = {
            "args": {"key": api_key, "sign": sign, "time": api_nonce},
            "op": "login",
        }
        self._ws.send(json.JSONEncoder.encode(message))

    def on_error(self, error):
        logger.error(WEBSOCKET_ERROR.format(repr(error)))
        self.stop()

    def on_close(self):
        if self._t._running:
            try:
                self.stop()
            except Exception as e:
                logger.error(WEBSOCKET_EXCEPTION_ON_CLOSE)
                logger.exception(e)
        else:
            logger.info(WEBSOCKET_CLOSED)

    def on_open(self):
        logger.info("on_open")
        self.get_token()

    def start(self):
        self._t = Thread(target=self._ws.run_forever)
        self._t.daemon = True
        self._t._running = True
        self._t.start()
        logger.debug(WEBSCOKED_STARTED)

    def stop(self):
        self._t._running = False
        self._ws.close()
        self._t.join()
        logger.debug(WEBSOCKET_STOPPED)

import logging
import json
from typing import Any
import websocket
import asyncio
import _thread
from threading import Thread
from decimal import Decimal
# from websocket import WebSocketApp

from hundi.lib.kairosdb.ticker import TickerKairosDbLib as Db
from hundi.writer.ticker import KairosDBTickerWriter as Writer
from hundi.config.message import (
    CONTRACT_SUBSCRIPTION_STATUS,
    SNAPSHOT_MESSAGE,
    SUBSCRIBED_TO_CHANNELS,
    UNKNOWN_MARKET_TYPE,
    WEBSCOKED_STARTED,
    WEBSOCKET_CLOSED,
    WEBSOCKET_ERROR,
    WEBSOCKET_EXCEPTION_ON_CLOSE,
    WEBSOCKET_STOPPED,
    UNKNOWN_PAIRS
)
from hundi.config.market import (
    MARKET_FTX_NAME,
    MARKET_FTX_WEBSOCKET_URL,
)
from hundi.config.ticker import TICKER_ACTION
from hundi.lib import helper
from hundi.model.ticker import TickerFutures as TickerFTX
from hundi.lib.executor import ExecutorLib as Executor

logger = logging.getLogger(__name__)


class TickerFtxCryptoAction():
    def __init__(self, market_type: str, pair: str) -> None:
        self.db = Db()
        self.writer = Writer(self.db)
        self.market_type = market_type.lower()
        self.pair = pair.lower()
        self.exchange = MARKET_FTX_NAME["spot"] if self.market_type == "spot" else MARKET_FTX_NAME["futures"]
        self.buffer = None
        self.ticker = None
        self.channel = None
        self.url = MARKET_FTX_WEBSOCKET_URL["spot"] if self.market_type == "spot" else MARKET_FTX_WEBSOCKET_URL["futures"]
        # self._executor = Executor()
        self.header = None
        self._thread = None
        self._ws = websocket.WebSocketApp(
            self.url,
            self.header,
            self.on_open,
            self.on_message,
            self.on_error,
            self.on_close)

    def on_open(self, ws: websocket.WebSocket):
        subscribe = json.dumps(
            {"op": "subscribe", "channel": "ticker", "market": self.pair.upper()}
        )
        logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))
        ws.send(subscribe)

    def on_message(self, ws: websocket.WebSocket, message: str) -> None:
        if self.buffer is None:
            self.buffer = json.loads(message)

            if len(self.buffer) > 0:
                if "type" in self.buffer:
                    type = self.buffer.get("type")
                    pair = self.buffer.get("market").lower()

                    if type == "subscribed":
                        logger.info(CONTRACT_SUBSCRIPTION_STATUS.format(type, pair))
                        self.channel = {"status": type}
                        self.buffer = None
                    elif type == "update":
                        logger.debug(SNAPSHOT_MESSAGE.format(message))

                        if pair != self.pair:
                            raise Exception('Pairs do not match.')

                        if self.get_ticker() is False:
                            raise Exception('No ticker')

                        if self.writer.write(
                                path=helper.get_metric_name(type="crypto", exchange=self.exchange, key=pair),
                                ticker=self.ticker) is False:
                            raise Exception("write error")
                        self.buffer = None
                        self.ticker = None
                else:
                    raise Exception("missing Market type")
            else:
                raise Exception("no message.")
        else:
            raise Exception("Message buffer not empty.")
        pass

    def on_error(self, ws: websocket.WebSocket, error: Any) -> None:
        logger.error(WEBSOCKET_ERROR.format(repr(error)))

        ws.close()

    def on_close(self, ws: websocket.WebSocket) -> None:
        ws.close()

    def get_ticker(self) -> bool:
        try:
            data = self.buffer.get("data")
            if data is None:
                return Exception("No data")

            bid_size = Decimal(data.get("bidSize"))
            ask_size = Decimal(data("ask_size"))
            # self.volumes[message["market"]] += bid_size + ask_size

            self.ticker = TickerFTX(
                timestamp=float(data["time"]),  # to float unix
                bid=Decimal(data["bid"]),
                ask=Decimal(data["ask"]),
                bid_size=bid_size,
                ask_size=ask_size,
                volume=0,
            )

            return True
        except Exception as e:
            logger.exception(e)

            return False

    # def stop(self):
    #     if self._thread and self._thread.is_alive:
    #         self._ws.close()
    #         self._thread.join()
    #         logger.debug(WEBSOCKET_STOPPED)

    # def run(self):
    #     asyncio.set_event_loop(self._loop)
    #     self._loop.run_forever()

    # def start(self) -> int:
    #     try:
    #         self._thread = Thread(target=self._ws.run_forever)
    #         self._thread.start()
    #         return self._thread.ident
    #         self._executor.run_async(func=self._ws.run_forever)
    #     except Exception or RuntimeError as e:
    #         logger.exception(e)
    #         return e

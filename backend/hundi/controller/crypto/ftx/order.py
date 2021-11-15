import datetime
import json
import logging
import websocket

from decimal import Decimal
from multiprocessing.dummy import Process as Thread

from hundi.config.message import (
    CONTRACT_SUBSCRIPTION_STATUS,
    ORDER_ATTRIBUTES,
    ORDER_MESSAGE,
    SUBSCRIBED_TO_CHANNELS,
    UNCLASSIFIED_MESSAGE,
    WEBSCOKED_STARTED,
    WEBSOCKET_CLOSED,
    WEBSOCKET_ERROR,
    WEBSOCKET_EXCEPTION_ON_CLOSE,
    WEBSOCKET_STOPPED,
)
from hundi.config.market import (
    MARKET_FTX_NAME,
    MARKET_FTX_PAIRS,
    MARKET_FTX_WEBSOCKET_URL,
)
from hundi.model.order import Order
from hundi.writer.order import KairosDBOrderWriter as Writer

logger = logging.getLogger(__name__)


class WebsockerOrder(object):
    def __init__(self, writer: Writer, market_type, pairs):
        self.writer = writer
        self.writer.exchange = (
            MARKET_FTX_NAME["SPOT"]
            if market_type == "spot"
            else MARKET_FTX_NAME["FUTURES"]
        )
        self.writer.market_type = market_type
        self.pairs = pairs
        self.market_type = market_type
        self.channels = {}
        self.bids = []
        self.asks = []

        self._ws = websocket.WebSocketApp(
            MARKET_FTX_WEBSOCKET_URL["SPOT"]
            if market_type == "spot"
            else MARKET_FTX_WEBSOCKET_URL["FUTURES"],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, message):
        message = json.loads(message)
        logger.debug(message)
        if "type" in message:
            if message.get("type") == "subscribed":
                logger.debug(
                    CONTRACT_SUBSCRIPTION_STATUS.format(
                        message.get("type"), message.get("market")
                    )
                )
                self.channels[message.get("market")] = {"status": message.get("type")}
            elif message.get("type") == "partial" or message.get("type") == "update":
                logger.debug(ORDER_MESSAGE.format(message))
                key = message["market"]
                for bid in message["data"]["bids"]:
                    self.writer.write_bid(
                        key,
                        self.get_order(
                            {
                                "timestamp": message["data"]["time"],
                                "side": "bid",
                                "price": bid[0],
                                "quantity": bid[1],
                            }
                        ),
                    )
                for ask in message["data"]["asks"]:
                    self.writer.write_ask(
                        key,
                        self.get_order(
                            {
                                "timestamp": message["data"]["time"],
                                "side": "ask",
                                "price": ask[0],
                                "quantity": ask[1],
                            }
                        ),
                    )
            else:
                logger.warning(UNCLASSIFIED_MESSAGE.format(message))

    def get_order(self, message):
        timestamp = float(message["timestamp"])  # to float unix
        side = message["side"]
        price = Decimal(message["price"])
        quantity = Decimal(message["quantity"])
        order = Order(timestamp=timestamp, side=side, price=price, quantity=quantity)
        logger.debug(
            ORDER_ATTRIBUTES.format(
                [datetime.datetime.fromtimestamp(timestamp), side, price, quantity]
            )
        )
        return order

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
        for pair in MARKET_FTX_PAIRS["FUTURES"]:
            subscribe = json.dumps(
                {"op": "subscribe", "channel": "orderbook", "market": pair}
            )
            logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))
            self._ws.send(subscribe)
        return

    @property
    def status(self):
        try:
            return self._t._running
        except Exception:
            return False

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

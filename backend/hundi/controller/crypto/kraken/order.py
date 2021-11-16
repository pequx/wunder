# import collections
import collections
import datetime
import json
import logging
import websocket

from decimal import Decimal
from multiprocessing.dummy import Process as Thread

from hundi.config.message import (
    CHANNEL_SYSTEM_STATUS,
    CONTRACT_SUBSCRIPTION_STATUS,
    HEARTBEAT_RECIVED,
    ORDER_ATTRIBUTES,
    ORDER_MESSAGE,
    ORDER_SNAPSHOT_FINISHED,
    SNAPSHOT_MESSAGE,
    SUBSCRIBED_TO_CHANNELS,
    UNCLASSIFIED_MESSAGE,
    UNKNOWN_MARKET_TYPE,
    WEBSCOKED_STARTED,
    WEBSOCKET_CLOSED,
    WEBSOCKET_ERROR,
    WEBSOCKET_EXCEPTION_ON_CLOSE,
    WEBSOCKET_STOPPED,
)
from hundi.config.market import (
    MARKET_KRAKEN_NAME,
    MARKET_KRAKEN_WEBSOCKET_URL,
)
from hundi.model.order import Order
from hundi.writer.order import KairosDBOrderWriter as Writer

logger = logging.getLogger(__name__)

OrderbookSpotData = collections.namedtuple(
    "Orderbook", ["channelID", "data", "channelName", "pair"]
)


class WebsocketOrderbook(object):
    def __init__(self, writer: Writer, market_type, pairs):
        self.writer = writer
        self.writer.exchange = (
            MARKET_KRAKEN_NAME["spot"]
            if market_type == "spot"
            else MARKET_KRAKEN_NAME["futures"]
        )
        self.writer.market_type = market_type
        self.channels = {}
        self.pairs = pairs
        self.market_type = market_type
        self._ws = websocket.WebSocketApp(
            MARKET_KRAKEN_WEBSOCKET_URL["spot"]
            if market_type == "spot"
            else MARKET_KRAKEN_WEBSOCKET_URL["futures"],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, message):
        message = json.loads(message)
        logger.debug(message)
        if self.market_type == "spot":
            if "event" in message:
                event = message.get("event")
                pair = message.get("pair")
                if event == "subscriptionStatus":
                    logger.info(CONTRACT_SUBSCRIPTION_STATUS.format(event, pair))
                    for product_id in pair:
                        self.channels[product_id] = {"status": event}
                elif event == "heartbeat":
                    logger.info(HEARTBEAT_RECIVED.format(event, pair))
                elif event is None:
                    data = OrderbookSpotData(message)
                    if data is not None and len(data) == 4:
                        return None
                    else:
                        logger.warning("empty message")
        elif self.market_type == "futures":
            if "event" in message:
                if message.get("event") == "info":
                    logger.info(
                        CHANNEL_SYSTEM_STATUS.format(
                            message.get("event", "unknown"),
                            message.get("version", "unknown"),
                        )
                    )
                if message.get("event") == "subscribed":
                    logger.info(
                        CONTRACT_SUBSCRIPTION_STATUS.format(
                            message.get("event"), message.get("product_ids")
                        )
                    )
                    for product_id in message.get("product_ids"):
                        self.channels[product_id] = {"status": message.get("event")}
            elif "event" not in message:
                if message.get("feed") == "book_snapshot":
                    logger.debug(SNAPSHOT_MESSAGE.format(message))
                    bids = []
                    asks = []
                    key = message["product_id"]
                    for bid in message["bids"]:
                        bids.append(
                            self.get_order(
                                {
                                    "timestamp": message["timestamp"],
                                    "side": "bid",
                                    "price": bid["price"],
                                    "qty": bid["qty"],
                                    "product_id": message["product_id"],
                                }
                            )
                        )
                    self.writer.snapshot(key, bids, "bid")
                    for ask in message["asks"]:
                        asks.append(
                            self.get_order(
                                {
                                    "timestamp": message["timestamp"],
                                    "side": "ask",
                                    "price": ask["price"],
                                    "qty": ask["qty"],
                                    "product_id": message["product_id"],
                                }
                            )
                        )
                    self.writer.snapshot(key, asks, "ask")
                    logger.info(
                        ORDER_SNAPSHOT_FINISHED.format(len(bids), format(len(asks)))
                    )
                elif message.get("feed") == "book":
                    logger.debug(ORDER_MESSAGE.format(message))
                    key = message["product_id"]
                    order = self.get_order(message)
                    if order.side == "bid" or order.side == "buy":
                        self.writer.write_bid(key, self.get_order(message))
                    elif order.side == "ask" or order.side == "sell":
                        self.writer.write_ask(key, self.get_order(message))
                else:
                    logger.warning(UNCLASSIFIED_MESSAGE.format(message))
        else:
            logger.warning(UNKNOWN_MARKET_TYPE.format(self.market_type))

    def get_order(self, message):
        timestamp = float(message["timestamp"] / 1000)  # to unix float
        side = message["side"]
        price = Decimal(message["price"])
        quantity = Decimal(message["qty"])
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
        if self.market_type == "spot":
            subscribe = json.dumps(
                {
                    "event": "subscribe",
                    "subscribe": {"name": "book"},
                    "pair": self.pairs,
                }
            )
            logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))
        elif self.market_type == "futures":
            subscribe = json.dumps(
                {
                    "event": "subscribe",
                    "feed": "book",
                    "product_ids": self.pairs,
                }
            )
            logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))
        else:
            logger.warning(UNKNOWN_MARKET_TYPE.format(self.market_type))
            return
        logger.debug(subscribe)
        self._ws.send(subscribe)

    @property
    def status(self):
        """
        Returns True if the websocket is running, False if not
        """
        try:
            return self._t._running
        except Exception:
            return False

    def start(self):
        """ Run the websocket in a thread """
        self._t = Thread(target=self._ws.run_forever)
        self._t.daemon = True
        self._t._running = True
        self._t.start()
        logger.info(WEBSCOKED_STARTED)

    def stop(self):
        """ Stop/join the websocket thread """
        self._t._running = False
        self._ws.close()
        self._t.join()
        logger.info(WEBSOCKET_STOPPED)

import datetime
import logging
from abc import ABC, abstractmethod
from typing import Union

from hundi.lib.kairosdb import order as kairosdb
from hundi.lib import helper
from hundi.config.message import (
    ORDER_ASKS_BUFFER_SIZE,
    ORDER_BIDS_BUFFER_SIZE,
    ORDER_WRITTEN,
    ORDERS_WRITTEN_COUNT,
    UNKNOWN_ORDER_SIDE,
)
from hundi.config.order import ORDER_BUFFER_SIZE
from hundi.model.order import Order

logger = logging.getLogger(__name__)


class OrderWriter(ABC):
    @abstractmethod
    def write(self, exchange, currency, asset, order: Order, timestamp):
        raise NotImplementedError


class TradeOutOfOrderException(Exception):
    pass


class DictionaryOrderWriter(OrderWriter):
    def __init__(self, output):
        self.output = output

    def write(self, key, order: Order):
        self.output.append(
            {
                "pair": key,
                "timestamp": datetime.datetime.fromtimestamp(order.timestamp),
                "side": order.side,
                "price": order.price,
                "quantity": order.quantity,
            }
        )
        logger.debug(
            ORDER_WRITTEN.format(
                key,
                datetime.datetime.fromtimestamp(order.timestamp),
                order.side,
                order.price,
                order.quantity,
            )
        )


class KairosDBOrderWriter(OrderWriter):
    def __init__(self):
        self.exchange = "default"
        self.type = "crypto"
        self.market_type = "default"
        self.bids_buffer = []
        self.asks_buffer = []
        self.count = 0
        self.type = "crypto"
        self.source = "order_writer.py"
        pass

    def write(self, key, order: Order):
        tags = {"source": self.source}

        if len(self.bids_buffer) > ORDER_BUFFER_SIZE:
            path = helper.get_metric_name(
                type=self.type, exchange=self.exchange, key=key, side="ask"
            )
            kairosdb.put_orders(path, self.bids_buffer, tags)
            logger.debug(ORDERS_WRITTEN_COUNT.format(self.count))
            self.bids_buffer = []
        elif len(self.asks_buffer) > ORDER_BUFFER_SIZE:
            path = helper.get_metric_name(
                type=self.type, exchange=self.exchange, key=key, side="bid"
            )
            kairosdb.put_orders(path, self.asks_buffer, tags)
            logger.debug(ORDERS_WRITTEN_COUNT.format(self.count))
            self.asks_buffer = []

        if order.side == "buy":
            self.bids_buffer.append(order)
            self.count += 1
            logger.debug(ORDER_ASKS_BUFFER_SIZE.format(len(self.asks_buffer)))
        elif order.side == "sell":
            self.asks_buffer.append(order)
            self.count += 1
            logger.debug(ORDER_BIDS_BUFFER_SIZE.format(len(self.bids_buffer)))
        else:
            logger.warning(UNKNOWN_ORDER_SIDE.format(order))

    def snapshot(self, key, orders: Union[str, Order], side):
        path = helper.get_metric_name(
            type=self.type, exchange=self.exchange, key=key, side=side
        )
        tags = {"source": self.source}
        kairosdb.put_orders(path, orders, tags)

    def write_ask(self, key, order: Order):
        tags = {"source": self.source}
        path = helper.get_metric_name(
            type=self.type, exchange=self.exchange, key=key, side="ask"
        )
        self.asks_buffer.append(order)
        self.count += 1
        if len(self.asks_buffer) > ORDER_BUFFER_SIZE:
            kairosdb.put_orders(path, self.asks_buffer, tags)
            logger.info(ORDERS_WRITTEN_COUNT.format(self.count))
            self.asks_buffer = []

    def write_bid(self, key, order: Order):
        tags = {"source": self.source}
        path = helper.get_metric_name(
            type=self.type, exchange=self.exchange, key=key, side="bid"
        )
        self.bids_buffer.append(order)
        self.count += 1
        if len(self.bids_buffer) > ORDER_BUFFER_SIZE:
            kairosdb.put_orders(path, self.bids_buffer, tags)
            logger.info(ORDERS_WRITTEN_COUNT.format(self.count))
            self.bids_buffer = []

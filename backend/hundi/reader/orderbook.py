import logging
from abc import ABC, abstractmethod

from hundi.lib import kairosdb
from hundi.config.message import (
    ORDER_ASKS_BUFFER_SIZE,
    ORDER_BIDS_BUFFER_SIZE,
    ORDER_WRITTEN,
    ORDERS_WRITTEN_COUNT,
    UNKNOWN_ORDER_SIDE,
)

# from hundi.market.data.models.order import Order as Entry

logger = logging.getLogger(__name__)


class OrderReader(ABC):
    @abstractmethod
    def read(self, exchange, key):
        raise NotImplementedError


class KairosDBOrderReader(OrderReader):
    def __init__(self, exchange="defualt"):
        self.exchange = exchange
        self.type = "crypto"
        self.source = "order_reader.py"
        pass

    def read(self, key):
        response = kairosdb.get_orderbook_as_dataframe(self.exchange, key)
        return response

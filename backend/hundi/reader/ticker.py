import logging
from abc import ABC, abstractmethod

from hundi.lib.kairosdb import ticker as kairosdb
# from hundi.config.ticker import (
#     TICKER_WRITTEN,
#     TICKERS_WRITTEN_COUNT,
# )

logger = logging.getLogger(__name__)


class TickerReader(ABC):
    @abstractmethod
    def read(self, exchange, key):
        raise NotImplementedError


class KairosDBTickerReader(TickerReader):
    def __init__(self, exchange, market_type):
        self.exchange = exchange
        self.type = "crypto"
        self.market_type = market_type
        self.source = "ticker_reader.py"
        pass

    def read(self, key):
        response = kairosdb.get_tickers_as_dataframe(
            self.type, self.exchange, self.market_type, key
        )
        return response

    def read_last(self, key):
        response = kairosdb.get_tickers_as_dataframe(
            type=self.type,
            exchange=self.exchange,
            market_type=self.market_type,
            metric_name=key,
            last=True,
        )
        return response

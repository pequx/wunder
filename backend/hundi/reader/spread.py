import logging
from abc import ABC, abstractmethod

# from hundi.lib import kairosdb

logger = logging.getLogger(__name__)


class SpreadReader(ABC):
    @abstractmethod
    def read(self, exchange, key):
        raise NotImplementedError


class KairosDBSpreadReader(SpreadReader):
    def __init__(self, type="futures", exchanges=[]):
        self.type = type
        self.exchanges = exchanges
        self.source = "spread_reader.py"
        pass

    # def read(self, key):
    #     response =

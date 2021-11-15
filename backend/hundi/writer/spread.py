import datetime
import logging
from abc import ABC, abstractmethod

import pandas as pd

from hundi.lib import helper
from hundi.lib.kairosdb import spread as kairosdb
from hundi.config.message import (
    SPREAD_WRITTEN,
    SPREAD_WRITTEN_COUNT,
    SPREADS_BUFFER_SIZE
)
from hundi.config.settings import SPREAD_BUFFER_SIZE, SPREAD_COLUMN_MAPPING
from hundi.model.spread import Spread

logger = logging.getLogger(__name__)


class SpreadWriter(ABC):
    @abstractmethod
    def write(self, exchanges, spread: Spread, timestamp):
        raise NotImplementedError


class DictionarySpreadWriter(SpreadWriter):
    def __init__(self, output):
        self.output = output

    def write(self, key, spread: Spread):
        self.output.append(
            {
                "pair": key,
                "timestamp": datetime.datetime.fromtimestamp(spread.timestamp),
                "value": spread.value,
            }
        )
        logger.debug(
            SPREAD_WRITTEN.format(
                key,
                datetime.datetime.fromtimestamp(spread.timestamp),
                spread.value
            )
        )


class KairosDBSpreadWriter(SpreadWriter):
    def __init__(self):
        # self.exchanges = exchanges
        # self.pairs = pairs
        self.spreads_buffer = []
        self.count = 0
        self.type = "crypto"
        self.source = "spread_writer.py"
        pass

    def write(self, key, spread: Spread):
        tags = {"source": self.source}

        if len(self.spreads_buffer) > SPREAD_BUFFER_SIZE:
            for exchange in self.exchanges:
                path = helper.get_metric_name(
                    type=self.type,
                    exchange=self.exchange,
                    key=self.key,
                    variant="spread",
                )
                kairosdb.put_spreads(path, self.spreads_buffer, tags)
                logger.debug(SPREAD_WRITTEN_COUNT.format(self.count))
            self.bids_buffer = []
        else:
            self.spreads_buffer.append(spread)
            self.count += 1
            logger.debug(SPREADS_BUFFER_SIZE.format(len(self.spreads_buffer)))

    def write_dataframe(
        self,
        spreads: pd.DataFrame,
        exchanges=[],
        pairs=[],
        column_mapping=False
    ):
        tags = {"source": self.source}
        # for i, exchange in enumerate(self.exchanges):
        #     self.exchanges[i] = helpers.format_metric_exchange(exchange)
        # for i, pair in enumerate(self.pairs):
        #     self.pairs[i] = helpers.format_metric_key(pair)
        metric_name = helper.get_spread_metric_name(
            type=self.type, exchanges=exchanges, pairs=pairs
        )
        logger.debug("ja {}".format(column_mapping))
        kairosdb.put_dataframe(
            metric_name=metric_name,
            f=spreads,
            tags=tags,
            column_mapping=(
                column_mapping if column_mapping is not False
                else SPREAD_COLUMN_MAPPING
            ),
        )
        self.count += 1
        logger.info(SPREAD_WRITTEN_COUNT.format(self.count))

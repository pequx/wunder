import logging

from typing import List

from hundi.config.settings import KAIROSDB_TTL
from hundi.config.order import (
    ORDER_DATAFRAME_TIME_UNIT,
    ORDER_START_RELATIVE,
    ORDER_END_RELATIVE,
    ORDER_DEFAULT_COLUMNS,
    ORDER_CACHE_TIME,
    ORDER_AGGREGATORS,
    ORDER_COLUMN_MAPPING
)
from hundi.lib.kairosdb import (
    datapoint,
    query
)
from hundi.lib import helper
from hundi.model.order import Order

logger = logging.getLogger(__name__)


def put_order(metric_name: str, order: Order, tags={}, ttl: int = KAIROSDB_TTL):
    for col in ORDER_COLUMN_MAPPING:
        timestamp = order.timestamp * 1000
        data = [[timestamp, float(order.get(col))]]
        t = tags
        t.update({"column": ORDER_COLUMN_MAPPING[col]})
        datapoint.put_datapoints(metric_name, data, tags=t, ttl=ttl)


def put_orders(
    metric_name: str,
    orders: List[Order],
    tags={},
    ttl: int = KAIROSDB_TTL
):
    for col in ORDER_COLUMN_MAPPING:
        data = []
        t = tags
        for order in orders:
            timestamp = order.timestamp * 1000
            data.append([timestamp, float(order.get(col))])
            t.update({"column": ORDER_COLUMN_MAPPING[col]})
        datapoint.put_datapoints(metric_name, data, tags=t, ttl=ttl)


def get_orderbook_as_dataframe(
    exchange: str,
    key,
    time_unit: str = ORDER_DATAFRAME_TIME_UNIT,
    start_relative: int = ORDER_START_RELATIVE,
    end_relative: int = ORDER_END_RELATIVE,
):
    try:
        asks = query.query_as_dataframe(
            metric_name=helper.get_metric_name(
                type="crypto", exchange=exchange, key=key, side="ask"
            ),
            time_unit=time_unit,
            columns=ORDER_DEFAULT_COLUMNS,
            start_relative=start_relative,
            end_relative=end_relative,
            cache_time=ORDER_CACHE_TIME,
            aggregators=ORDER_AGGREGATORS["MIN"][time_unit.upper()]
        )
        bids = query.query_as_dataframe(
            metric_name=helper.get_metric_name(
                type="crypto", exchange=exchange, key=key, side="bid"
            ),
            time_unit=time_unit,
            columns=ORDER_DEFAULT_COLUMNS,
            start_relative=start_relative,
            end_relative=end_relative,
            cache_time=ORDER_CACHE_TIME,
            aggregators=ORDER_AGGREGATORS["MAX"][time_unit.upper()]
        )
    except Exception as e:
        logger.warning("orderbook exception {}".format(e))
    finally:
        orderbook = asks.join(
            bids, how="outer", lsuffix="_ask", rsuffix="_bid"
        )
        logger.debug("orderbook {}".format(orderbook))
        return orderbook

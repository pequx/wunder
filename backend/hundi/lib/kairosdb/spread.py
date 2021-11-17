from types import Union

from hundi.model.spread import Spread
from hundi.config.settings import KAIROSDB_TTL
from hundi.config.spread import SPREAD_COLUMN_MAPPING
from hundi.config.order import ORDER_COLUMN_MAPPING
from hundi.lib.kairosdb import datapoint


def put_spreads(
    metric_name: str,
    spreads: Union[str, Spread],
    tags={},
    ttl: int = KAIROSDB_TTL
):
    for col in SPREAD_COLUMN_MAPPING:
        data = []
        t = tags
        for spread in spreads:
            timestamp = spread.timestamp
            data.append([timestamp, float(spread.get(col))])
            t.update({"column": ORDER_COLUMN_MAPPING[col]})
        datapoint.put_datapoints(metric_name, data, tags=t, ttl=ttl)

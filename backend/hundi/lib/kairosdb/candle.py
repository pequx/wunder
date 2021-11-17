from types import Union

from hundi.config.settings import KAIROSDB_TTL
from hundi.config.candle import CANDLE_COLUMN_MAPPING
from hundi.model.candle import Candle
from hundi.lib.kairosdb import datapoint


def put_candle(metric_name, candle: Candle, tags={}, ttl=KAIROSDB_TTL):
    for col in CANDLE_COLUMN_MAPPING:
        timestamp = candle.timestamp * 1000
        # KairosDB timestamp is in milliseconds
        data = [[timestamp, float(candle.get(col))]]
        t = tags
        t.update({"column": CANDLE_COLUMN_MAPPING[col]})
        datapoint.put_datapoints(metric_name, data, tags=t, ttl=ttl)


def put_candles(
    metric_name,
    candles: Union[str, Candle],
    tags={},
    ttl=KAIROSDB_TTL
):
    for col in CANDLE_COLUMN_MAPPING:
        data = []
        t = tags
        for candle in candles:
            timestamp = candle.timestamp * 1000
            data.append([timestamp, float(candle.get(col))])
            t.update({"column": CANDLE_COLUMN_MAPPING[col]})
        datapoint.put_datapoints(metric_name, data, tags=t, ttl=ttl)

import logging

from typing import List

from hundi.config.settings import KAIROSDB_TTL
from hundi.config.ticker import (
    TICKER_COLUMN_MAPPING,
    TICKER_DATAFRAME_TIME_UNIT,
    TICKER_START_RELATIVE,
    TICKER_END_RELATIVE,
    TICKER_DEFAULT_COLUMNS,
    TICKER_CACHE_TIME,
    TICKER_AGGREGATORS
)
from hundi.lib.kairosdb import datapoint
from hundi.lib.kairosdb import query
from hundi.lib import helper
from hundi.model.ticker import TickerFutures, TickerSpot

logger = logging.getLogger(__name__)


class TickerKairosDbLib():
    def put_ticker(self, path: str, ticker: TickerSpot or TickerFutures, tags={}, ttl: int = KAIROSDB_TTL):
        try:
            market_type = helper.get_market_type(path)
            mapping = TICKER_COLUMN_MAPPING[market_type]
            for column in mapping:
                timestamp = ticker.timestamp * 1000
                # KairosDB timestamp is in milliseconds
                t = tags
                t.update({"column": mapping[column]})
                if datapoint.put_datapoints(
                        metric_name=path, datapoints=[[timestamp, float(ticker.get(column))]],
                        tags=t, ttl=ttl) is False:
                    return Exception('')
                return True
        except Exception as e:
            logger.exception(e)
            return False

    def put_tickers(self, path: str, tickers: List[TickerSpot or TickerFutures], tags={}, ttl: int = KAIROSDB_TTL):
        try:
            for ticker in tickers:
                self.put_ticker(path, ticker, tags, ttl)
                return True
        except Exception as e:
            logger.exception(e)
            return False

    def get_tickers_as_dataframe(
        type: str,
        exchange: str,
        market_type: str,
        metric_name: str,
        time_unit: str = TICKER_DATAFRAME_TIME_UNIT,
        start_relative: int = TICKER_START_RELATIVE,
        end_relative: int = TICKER_END_RELATIVE,
        last: bool = False,
    ):
        try:
            tickers = query.query_as_dataframe(
                metric_name=helper.get_metric_name(
                    type=type,
                    exchange=exchange,
                    key=metric_name,
                    # period=(interval if interval > 0 else None),
                    # variant=("ticker" if interval == 0 else None),
                    variant="ticker",
                ),
                columns=TICKER_DEFAULT_COLUMNS[market_type.upper()],
                time_unit=time_unit,
                start_relative=start_relative,
                end_relative=end_relative,
                cache_time=TICKER_CACHE_TIME,
                aggregators=(
                    TICKER_AGGREGATORS["LAST"]
                    if last is True
                    else TICKER_AGGREGATORS["AVG"][time_unit.upper()]
                ),
            )
        except Exception as e:
            logger.warning("ticker exception {}".format(e))
        finally:
            logger.debug("tickers {}".format(tickers))
            return tickers

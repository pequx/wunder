TICKER_COLUMNS = {"spot": ["channelID", "points", "channelName", "pair"]}
TICKER_DEFAULT_COLUMNS = {
    "spot": ["b", "a", "bs", "as", "v"],
    "futures": ["b", "a", "bs", "as", "v"],
}
TICKER_COLUMN_MAPPING = {
    "spot": {
        "bid": "b",
        "ask": "a",
        "bid_size": "bs",
        "ask_size": "as",
        "volume": "v",
    },
    "futures": {
        "bid": "b",
        "ask": "a",
        "bid_size": "bs",
        "ask_size": "as",
        "volume": "v",
    },
}
TICKER_SLOTS = {
    "spot": ["timestamp", "open", "high", "low", "close", "volume"],
    "futures": ["timestamp", "bid", "ask", "bid_size", "ask_size", "volume"],
    "FTX": ["timestamp", "bid", "ask", "bid_size", "ask_size"]
}
TICKER_START_RELATIVE = 1
TICKER_END_RELATIVE = 0
TICKER_CACHE_TIME = 300
TICKERS_BUFFER_SIZE = 100
TICKER_OHLC_COLUMNS = {
    "spot": [
        "time",
        "etime",
        "open",
        "high",
        "low",
        "close",
        "vwap",
        "volume",
        "count"
    ]
}
TICKER_DATAFRAME_TIME_UNIT = "minutes"
TICKER_AGGREGATOR_TIME_UNIT = "milliseconds"
TICKER_AGGREGATORS = {
    "MAX": {
        "MILLISECONDS": [
            {"name": "max", "sampling": {"value": "1", "unit": "milliseconds"}}
        ],
        "SECONDS": [
            {"name": "max", "sampling": {"value": "1", "unit": "seconds"}}
        ],
        "MINUTES": [
            {"name": "max", "sampling": {"value": "1", "unit": "minutes"}}
        ],
        "HOURS": [
            {"name": "max", "sampling": {"value": "1", "unit": "hours"}}
        ]
    },
    "AVG": {
        "MILLISECONDS": [
            {"name": "avg", "sampling": {"value": "1", "unit": "milliseconds"}}
        ],
        "SECONDS": [
            {"name": "avg", "sampling": {"value": "1", "unit": "seconds"}}
        ],
        "MINUTES": [
            {"name": "avg", "sampling": {"value": "1", "unit": "minutes"}}
        ],
        "HOURS": [
            {"name": "avg", "sampling": {"value": "1", "unit": "hours"}}
        ]
    },
    "LAST": [
        {
            "name": "last",
            "sampling": {"value": "1", "unit": "years"},
            "align_end_time": True,
        }
    ],
}
TICKER_CACHE_TIME = 300

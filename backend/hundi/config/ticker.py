TICKER_COLUMNS = {"SPOT": ["channelID", "points", "channelName", "pair"]}
TICKER_DEFAULT_COLUMNS = {
    "SPOT": ["b", "a", "bs", "as", "v"],
    "FUTURES": ["b", "a", "bs", "as", "v"],
}
TICKER_COLUMN_MAPPING = {
    "SPOT": {
        "bid": "b",
        "ask": "a",
        "bid_size": "bs",
        "ask_size": "as",
        "volume": "v",
    },
    "FUTURES": {
        "bid": "b",
        "ask": "a",
        "bid_size": "bs",
        "ask_size": "as",
        "volume": "v",
    },
}
TICKER_SLOTS = {
    "SPOT": ["timestamp", "open", "high", "low", "close", "volume"],
    "FUTURES": ["timestamp", "bid", "ask", "bid_size", "ask_size", "volume"],
    "FTX": ["timestamp", "bid", "ask", "bid_size", "ask_size"]
}
TICKER_START_RELATIVE = 1
TICKER_END_RELATIVE = 0
TICKER_CACHE_TIME = 300
TICKERS_BUFFER_SIZE = 100
TICKER_OHLC_COLUMNS = {
    "SPOT": [
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

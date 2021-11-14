CANDLE_DEFAULT_COLUMNS = ["open", "high", "low", "close", "volume"]
CANDLE_COLUMN_MAPPING = {
    "open": "o",
    "high": "h",
    "low": "l",
    "close": "c",
    "volume": "v",
}
CANDLE_TIME_UNIT = "minutes"
CANDLE_START_RELATIVE = 5
CANDLE_END_RELATIVE = 0
CANDLE_CACHE_TIME = 300
CANDLE_PERIODS = {
    "5s": 5,
    "1m": 60,
    "5m": 5 * 60,
    "15m": 15 * 60,
    "1h": 1 * 60 * 60,
    "4h": 4 * 60 * 60,
    "1d": 24 * 60 * 60,
    "1w": 7 * 24 * 60 * 60,
    "1M": 30 * 24 * 60 * 60,
}
CANDLE_BUFFER_SIZE = 1
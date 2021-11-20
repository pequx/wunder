from decouple import config

"""
KRAKEN
"""
MARKET_KRAKEN_NAME = {"spot": "Spot Kraken", "futures": "Futures Kraken"}
MARKET_KRAKEN_WEBSOCKET_URL = {
    "spot": "wss://ws.kraken.com/",
    "futures": "wss://futures.kraken.com/ws/v1/",
}
MARKET_KRAKEN_REST_URL = {
    "futures": {"SEND_ORDER": "https://futures.kraken.com/derivatives/v3/sendorder"}
}
MARKET_KRAKEN_TOKEN_URL = "https://api.kraken.com/0/private/GetWebSocketsToken"
MARKET_KRAKEN_TOKEN_PATH = b"/0/private/GetWebSocketsToken"
MARKET_KRAKEN_PAIRS = {
    "spot": [
        "XBT/USD",
        # "XRP/USD"
    ],
    "futures": [
        # "PI_XBTUSD",
        "FI_XBTUSD_210625"
    ],
}
MARKET_KRAKEN_INTERVAL = {"spot": 1, "futures": 1}
MARKET_KRAKEN_API_KEY = config("MARKET_KRAKEN_API_KEY", False)
MARKET_KRAKEN_API_SIGN = config("MARKET_KRAKEN_API_SIGN", False)

"""
FTX
"""
MARKET_FTX_NAME = {"spot": "Spot FTX", "futures": "Futures FTX"}
MARKET_FTX_WEBSOCKET_URL = {"spot": "wss://ftx.com/ws/", "futures": "wss://ftx.com/ws/"}
MARKET_FTX_REST_URL = {
    "spot": {"SNAPSHOT": "https://ftx.com/api/markets/"},
    "futures": {"SNAPSHOT": "https://ftx.com/api/futures/"},
}
MARKET_FTX_PAIRS = {
    "spot": [],
    "futures": [
        # "BTC-0326",
        "BTC-0625"
    ],
}
MARKET_FTX_INTERVAL = {"spot": 1, "futures": 1}
MARKET_FTX_API_KEY = config("MARKET_FTX_API_KEY", False)
MARKET_FTX_API_SECRET = config("MARKET_FTX_API_SECRET", False)
MARKET_FTX_CHANNEL = {
    "markets": {},
    "ticker": {}
}
MARKET_FTX_SUBSCRIPTION = {
    "markets": {"op": "subscribe", "channel": "markets"},
    "ticker": {"op": "subscribe", "channel": "ticker", "market": None}
}

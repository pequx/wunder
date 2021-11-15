from decouple import config

"""
KRAKEN
"""
MARKET_KRAKEN_NAME = {"SPOT": "Spot Kraken", "FUTURES": "Futures Kraken"}
MARKET_KRAKEN_WEBSOCKET_URL = {
    "SPOT": "wss://ws.kraken.com/",
    "FUTURES": "wss://futures.kraken.com/ws/v1/",
}
MARKET_KRAKEN_REST_URL = {
    "FUTURES": {"SEND_ORDER": "https://futures.kraken.com/derivatives/v3/sendorder"}
}
MARKET_KRAKEN_TOKEN_URL = "https://api.kraken.com/0/private/GetWebSocketsToken"
MARKET_KRAKEN_TOKEN_PATH = b"/0/private/GetWebSocketsToken"
MARKET_KRAKEN_PAIRS = {
    "SPOT": [
        "XBT/USD",
        # "XRP/USD"
    ],
    "FUTURES": [
        # "PI_XBTUSD",
        "FI_XBTUSD_210625"
    ],
}
MARKET_KRAKEN_INTERVAL = {"SPOT": 1, "FUTURES": 1}
MARKET_KRAKEN_API_KEY = config("MARKET_KRAKEN_API_KEY", False)
MARKET_KRAKEN_API_SIGN = config("MARKET_KRAKEN_API_SIGN", False)

"""
FTX
"""
MARKET_FTX_NAME = {"SPOT": "Spot FTX", "FUTURES": "Futures FTX"}
MARKET_FTX_WEBSOCKET_URL = {"SPOT": "wss://ftx.com/ws/", "FUTURES": "wss://ftx.com/ws/"}
MARKET_FTX_REST_URL = {
    "SPOT": {"SNAPSHOT": "https://ftx.com/api/markets/"},
    "FUTURES": {"SNAPSHOT": "https://ftx.com/api/futures/"},
}
MARKET_FTX_PAIRS = {
    "SPOT": [],
    "FUTURES": [
        # "BTC-0326",
        "BTC-0625"
    ],
}
MARKET_FTX_INTERVAL = {"SPOT": 1, "FUTURES": 1}
MARKET_FTX_API_KEY = config("MARKET_FTX_API_KEY", False)
MARKET_FTX_API_SECRET = config("MARKET_FTX_API_SECRET", False)
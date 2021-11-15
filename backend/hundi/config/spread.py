SPREAD_DEFAULT_COLUMNS = ["v1", "v2"]
SPREAD_COLUMN_MAPPING = {
    "s_ask": "v1",
    "s_bid": "v2",
}
SPREAD_THRESHOLDS = {
    "FUTURES": {
        "s5": ">0",
        "s6": "<0",
        "s7": ">0",
        "s8": "<0"
    }
}
SPREAD_BUFFER_SIZE = 100
SPREAD_WRITE_INTERVAL = 60
SPREAD_AGGREGATOR_TIME_UNIT = "milliseconds"
SPREAD_DATAFRAME_TIME_UNIT = "minutes"
SPREAD_START_RELATIVE = 1
SPREAD_END_RELATIVE = 0
SPREAD_CACHE_TIME = 300
SPREAD_AGGREGATORS = {
    "ASKS": [
        {"name": "max", "sampling": {"value": "1", "unit": SPREAD_AGGREGATOR_TIME_UNIT}}
    ],
    "BIDS": [
        {"name": "max", "sampling": {"value": "1", "unit": SPREAD_AGGREGATOR_TIME_UNIT}}
    ],
}
SPREAD_NAMES = ["Spread 1", "Spread 2", "Spread 3", "Spread 4"]
# SPREAD_MARKET_PAIRS = {
#     'SPOT': []
#     'FUTURES': {
#         [MARKET_KRAKEN_NAME['FUTURES']]: [

#         ]
#     }
#         "FI_XBTUSD_210625",
#         "BTC-0625"
#     ]
# }
# SPREAD_EXCHANGE_PAIRS = {
#     'SPOT': [],
#     'FUTURES': [
#         MARKET_KRAKEN_NAME['FUTURES'],
#         MARKET_FTX_NAME['FUTURES']
#     ]
# }

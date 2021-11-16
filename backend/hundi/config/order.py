ORDER_DEFAULT_COLUMNS = ["p", "q"]
ORDER_COLUMN_MAPPING = {"price": "p", "quantity": "q"}
ORDER_BUFFER_SIZE = 100
ORDER_TIME_UNIT = "milliseconds"
ORDER_START_RELATIVE = 1
ORDER_END_RELATIVE = 0
ORDER_CACHE_TIME = 300
ORDER_DATAFRAME_TIME_UNIT = "minutes"
ORDER_AGGREGATOR_TIME_UNIT = "milliseconds"
ORDER_AGGREGATORS = {
    "MIN": {
        "MILLISECONDS": [
            {"name": "min", "sampling": {"value": "1", "unit": "milliseconds"}}
        ],
        "SECONDS": [
            {"name": "min", "sampling": {"value": "1", "unit": "seconds"}}
        ],
        "MINUTES": [
            {"name": "min", "sampling": {"value": "1", "unit": "minutes"}}
        ],
        "HOURS": [
            {"name": "min", "sampling": {"value": "1", "unit": "hours"}}
        ]
    },
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
# ORDERBOOK_COLUMNS = {
#     "spot": ["channelID", "data", "channelName", "pair"]
# }
# ORDERBOOK_ASK_COLUMNS = {
#     "spot": ["channelID", "data", "channelName", "pair"]
# }

from datetime import datetime, timezone
from typing import Dict, List

from hundi.config.message import UNKNOWN_MARKET_TYPE
from hundi.config.settings import ENVIRONMENT
from hundi.config.metric import METRIC_CRYPTO
from hundi.config.market import (
    MARKET_FTX_NAME,
    MARKET_FTX_WEBSOCKET_URL,
    MARKET_KRAKEN_NAME,
    MARKET_KRAKEN_WEBSOCKET_URL
)


def get_timestamp() -> float:
    return datetime.now(timezone.utc).timestamp()


def get_pairs(pairs: str) -> List[str]:
    return pairs.upper().split(",")


def get_exchanges_names(exchanges: str, type: str = "spot") -> List[str]:
    n = []
    for exchange in exchanges.split(",", 1):
        e = exchange.lower()
        t = type.upper()
        if e == "kraken":
            n.append(MARKET_KRAKEN_NAME[t])
        elif e == "ftx":
            n.append(MARKET_FTX_NAME[t])
    if len(n) < 1:
        raise Exception("No exchange match.")
    return n


# def get_exchange_name(exchange: str) -> str:


def get_exchange_url(exchange: str, type: str = "spot") -> str:
    e = exchange.lower()
    t = type.upper()
    if e == "kraken":
        return MARKET_KRAKEN_WEBSOCKET_URL[t]
    elif e == "ftx":
        return MARKET_FTX_WEBSOCKET_URL[t]


def format_exchange(string=""):
    return string.replace(" ", ".").replace("-", "_").lower()


def format_market(name=""):
    return name.replace("/", "_").replace("-", "_").lower()

# development.hundi.crypto.spot.ftx.abnb_1231.ticker


def get_market_type(path: str or object) -> str:
    if path is str:
        return path.split('.')[3]

        # def get_market(path: str):
        #     return format_market(path.split('.')[4])

        # def get_markets(paths: List[object]):
        #     markets = []
        #     for name in paths:
        #         path = paths[name]
        #         markets.append(path['name'])
        #     return markets


def format_name(name: str) -> str:
    return name.replace("/", "_").replace("-", "_").lower()

# def get_path(market: str, paths: List[str]):
#     path = ""
#     for index in enumerate(paths):
#         path = paths[index]
#         if market != get_market(market):
#             return
#         return path


def format_path(path: Dict) -> str:
    return METRIC_CRYPTO.format(
        path['type'],
        path['exchange'],
        path['market_type'],
        format_name(path['market']),
        path['variant'])


def get_subscription(paths: object) -> str:
    for name in paths:
        path = paths[name]
        if path['variant'] == "subscription":
            return path['market']
        elif path['market'] == "markets" and path['variant'] == "":
            return "markets"


def get_url(paths: object) -> str:
    for name in paths:
        path = paths[name]
        exchange = path['exchange']
        market_type = path['market_type']

        if exchange == "ftx":
            return MARKET_FTX_WEBSOCKET_URL[market_type]


def get_paths(type: str, exchange: str, market_type: str, markets: str, variant: str = "") -> object:
    type = type.lower()
    markets = markets.split(',')
    market_type = market_type.lower()
    paths = {}
    if type == "crypto":
        for market in markets:
            paths[format_name(market)] = {
                "type": type,
                "exchange": exchange.lower(),
                "market_type": market_type.lower(),
                "market": market.lower(),
                "variant": variant.lower()
            }
    return paths


def get_metric_name(type: str, exchange: str, market_type: str, market: str, variant: str) -> str:
    if type == "crypto":
        # Metric_name: hundi.crypto.kraken.spot.xbt_usd.ticker
        name = METRIC_CRYPTO.format(
            type,
            format_exchange(exchange),
            market_type,
            format_market(market),
            variant.lower()
        ).lower()
        return name
    else:
        raise ValueError(UNKNOWN_MARKET_TYPE.format(type))


def get_spread_metric_name(type="", exchanges=[], pairs=[]):
    return get_metric_name(
        type=type,
        exchange=".".join(exchanges),
        key=".".join(pairs),
        variant="spread",
    )


def get_order_metric_name(type="", exchange="", pair=""):
    return get_metric_name(
        type=type,
        exchange=exchange,
        key=pair,
        variant="order"
    )


def get_metric_subkey(period: int = 0, variant: str = None, side: str = None):
    if period > 0:
        return "{}{}".format(period, "s").lower()
    if side == "ask" or side == "sell":
        return "asks"
    elif side == "bid" or side == "buy":
        return "bids"
    if variant == "spread":
        return "spread"
    if variant == "ticker":
        return "ticker"


# def get_spread_column_mapping():
#     column_mapping = {}
#     for i, spread in enumerate(SPREAD_NAMES):
#         column_mapping[spread] = SPREAD_COLUMN_MAPPING['value_{}' . format(i + 1)]
#     return column_mapping


def get_sprad_suffixes(exchanges, pairs):
    lsuffix = ".{}.{}".format(
        format_exchange(exchanges[0]),
        format_market(pairs[0]),
    )
    rsuffix = ".{}.{}".format(
        format_metric_exchange(exchanges[1]),
        format_metric_key(pairs[1]),
    )
    return {"l": lsuffix, "r": rsuffix}


def reverse_dict(dict):
    return {v: k for k, v in dict.items()}


def get_spread_column_mapping(market_1, market_2):
    return {
        "s1": "s_price_bid{}.orderbook.spread_1.s_price_bid{}".format(
            market_1, market_2
        ),
        "s2": "s_price_bid{}.orderbook.spread_2.s_price_bid{}".format(
            market_2, market_1
        ),
        "s3": "s_price_ask{}.orderbook.spread_3.s_price_ask{}".format(
            market_1, market_2
        ),
        "s4": "s_price_ask{}.orderbook.spread_4.s_price_ask{}".format(
            market_2, market_1
        ),
        "s5": "s_price_bid{}.orderbook.spread_5.s_price_ask{}".format(
            market_1, market_2
        ),
        "s6": "s_price_ask{}.orderbook.spread_6.s_price_bid{}".format(
            market_2, market_1
        ),
        "s7": "s_price_bid{}.orderbook.spread_7.s_price_ask{}".format(
            market_1, market_2
        ),
        "s8": "s_price_ask{}.orderbook.spread_8.s_price_bid{}".format(
            market_2, market_1
        ),
        "s9": "s_bid{}.ticker.spread_9.s_bid{}".format(market_1, market_2),
        "s10": "s_bid{}.ticker.spread_10.s_bid{}".format(market_2, market_1),
        "s11": "s_ask{}.ticker.spread_11.s_ask{}".format(market_1, market_2),
        "s12": "s_ask{}.ticker.spread_12.s_ask{}".format(market_2, market_1),
        "s13": "s_bid{}.ticker.spread_13.s_ask{}".format(market_1, market_2),
        "s14": "s_ask{}.ticker.spread_14.s_bid{}".format(market_2, market_1),
        "s15": "s_bid{}.ticker.spread_15.s_ask{}".format(market_1, market_2),
        "s16": "s_ask{}.ticker.spread_16.s_bid{}".format(market_2, market_1),
    }

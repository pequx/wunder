import logging
import time
from multiprocessing.dummy import Process as Thread
import pandas as pd

from hundi.lib import helper
from hundi.config.message import SPREAD_STARTED, SPREAD_STOPPED
from hundi.config.spread import SPREAD_WRITE_INTERVAL
from hundi.reader.order import KairosDBOrderReader as OrderReader
from hundi.reader.ticker import KairosDBTickerReader as TickerReader
from hundi.writer.spread import KairosDBSpreadWriter as SpreadWriter

logger = logging.getLogger(__name__)


class SpreadController(Thread):
    def __init__(
        self,
        writer: SpreadWriter,
        order_reader: OrderReader,
        ticker_reader: TickerReader,
        exchanges,
        market_type,
        pairs,
        spreads
    ):
        try:
            self.writer = writer
            if len(exchanges) > 2:
                raise Exception("wrong size")
            elif len(pairs) < 2 or len(pairs) % 2 != 0:
                raise Exception("no")
            self.exchanges = exchanges
            self.pairs = pairs
            self.market_type = market_type
            self.is_running = False
            self.orders_buffer = None
            self.tickers_buffer = None
            self.order_readers = self.get_order_readers(order_reader)
            self.ticker_readers = self.get_ticker_readers(ticker_reader)
            self.orders = None
            self.tickers = None
            self.spreads = None
            self.metrics = None
            self.signals = None
            self.suffixes = helper.get_sprad_suffixes(
                self.exchanges, self.pairs
            )
            self.spreads_default_columns = spreads
            self.spreads_column_mapping = helper.get_spread_column_mapping(
                self.suffixes["l"], self.suffixes["r"]
            )
            logger.debug("Order readers: {}".format(self.order_readers))
        except Exception as e:
            logger.error("Init exception {}".format(e))

    def get_ticker_readers(self, ticker_reader: TickerReader):
        try:
            readers = {}
            if len(self.pairs) % 2 == 0:
                if len(self.pairs) == 2:
                    for i, pair in enumerate(self.pairs):
                        exchange = self.exchanges[i]
                        logger.debug("ex {} pair {}".format(exchange, pair))
                        reader: TickerReader = ticker_reader(
                            exchange, self.market_type
                        )
                        logger.debug("new ticker reader {}".format(reader))
                        readers[exchange] = {}
                        readers[exchange][pair] = reader
                else:
                    raise Exception("computer says no.1")
            else:
                raise Exception("computer says no.")
            logger.debug(readers)
            return readers
        except Exception as e:
            logger.error("Get order readers expcetion {}".format(e))

    def get_order_readers(self, order_reader: OrderReader):
        try:
            readers = {}
            if len(self.pairs) % 2 == 0:
                if len(self.pairs) == 2:
                    for i, pair in enumerate(self.pairs):
                        exchange = self.exchanges[i]
                        logger.debug("ex {} pair {}".format(exchange, pair))
                        new = order_reader(exchange)
                        logger.debug("new order reader {}".format(new))
                        readers[exchange] = {}
                        readers[exchange][pair] = new
                else:
                    raise Exception("computer says no.1")
            else:
                raise Exception("computer says no.")
            logger.debug(readers)
            return readers
        except Exception as e:
            logger.error("Get order readers expcetion {}".format(e))

    def get_orderbooks(self):
        self.orders_buffer = {}
        for i, pair in enumerate(self.pairs):
            exchange = self.exchanges[i]
            reader: OrderReader = self.order_readers[exchange][pair]
            response = reader.read(key=pair)
            self.orders_buffer[exchange] = {}
            self.orders_buffer[exchange][pair] = response
            logger.debug("orders_buffer.append {}".format(pair))
        logger.debug("get_orderbooks {}".format(self.orders_buffer))

    def get_tickers(self, last=False):
        self.tickers_buffer = {}
        for i, pair in enumerate(self.pairs):
            exchange = self.exchanges[i]
            reader: TickerReader = self.ticker_readers[exchange][pair]
            response = (
                reader.read_last(pair)
                if last
                else reader.read(pair)
            )
            logger.debug(response)
            self.tickers_buffer[exchange] = {}
            self.tickers_buffer[exchange][pair] = response
            logger.debug("tickers_buffer.append {}".format(pair))
        logger.debug("get_tickers {}".format(self.tickers_buffer))

    def get_spreads(self):
        market_1 = self.suffixes["l"]
        market_2 = self.suffixes["r"]
        # cena bidu z tickera giełdy 1, kraken
        market_1_ticker_bid = "b{}".format(market_1)
        # cena bidu z orderbooka giełdy 1, kraken
        market_1_orderbook_bid = "p_bid{}".format(market_1)
        # market_1_orderbook_quantity_bid = "q_bid{}".format(market_1)
        # cena aska z tickera giełdy 1, kraken
        market_1_ticker_ask = "a{}".format(market_1)
        # cena aska z orderbooka giełdy 1, kraken
        market_1_orderbook_ask = "p_ask{}".format(market_1)
        # market_1_orderbook_quantity_ask = "q_ask{}".format(market_1)
        # cena aska z tickera giełdy 2, ftx
        market_2_ticker_ask = "a{}".format(market_2)
        # cena aska z orderbooka giełdy 2, ftx
        market_2_orderbook_ask = "p_ask{}".format(market_2)
        # market_2_orderbook_quantity_ask = "q_ask{}".format(market_2)
        # cena bidu z tickera giełdy 2, ftx
        market_2_ticker_bid = "b{}".format(market_2)
        # cena bidu z orderbooka giełdy 2, ftx
        market_2_orderbook_bid = "p_bid{}".format(market_2)
        # market_2_orderbook_quantity_bid = "q_bid{}".format(market_1)

        self.spreads = (
            self.orders.join(
                self.tickers, how="outer"
            ).sort_index().bfill().ffill()
        )
        self.orders = None
        self.tickers = None

        for column in self.spreads_default_columns:
            # bid z gieldy 1 vs. bid z gieldy 2
            if column == "s1":
                self.spreads[self.spreads_column_mapping["s1"]] = (
                    100
                    - (
                        self.spreads[market_1_orderbook_bid]
                        * 100
                        / self.spreads[market_2_orderbook_bid]
                    )
                    if self.spreads[market_1_orderbook_bid] is not None
                    and self.spreads[market_2_orderbook_bid] is not None
                    else 0
                )
            elif column == "s2":
                # bid z gieldy 2 vs. bid z gieldy 1
                self.spreads[self.spreads_column_mapping["s2"]] = (
                    100
                    - (
                        self.spreads[market_2_orderbook_bid]
                        * 100
                        / self.spreads[market_1_orderbook_bid]
                    )
                    if self.spreads[market_2_orderbook_bid] is not None
                    and self.spreads[market_1_orderbook_bid] is not None
                    else 0
                )
            elif column == "s3":
                # ask z gieldy 1 vs. ask z gieldy 2
                self.spreads[self.spreads_column_mapping["s3"]] = (
                    100
                    - (
                        self.spreads[market_1_orderbook_ask]
                        * 100
                        / self.spreads[market_2_orderbook_ask]
                    )
                    if self.spreads[market_1_orderbook_ask] is not None
                    and self.spreads[market_2_orderbook_ask] is not None
                    else 0
                )
            elif column == "s4":
                # ask z gieldy 2 vs. ask z gieldy 1
                self.spreads[self.spreads_column_mapping["s4"]] = (
                    100 - (
                        self.spreads[market_2_orderbook_ask]
                        * 100
                        / self.spreads[market_1_orderbook_ask]
                    )
                    if self.spreads[market_2_orderbook_ask] is not None
                    and self.spreads[market_1_orderbook_ask] is not None
                    else 0
                )
            elif column == "s5":
                # bid z gieldy 1 vs. ask z gieldy 2
                # kupno do sprzedazy
                self.spreads[self.spreads_column_mapping["s5"]] = (
                    100
                    - (
                        self.spreads[market_1_orderbook_bid]
                        * 100
                        / self.spreads[market_2_orderbook_ask]
                    )
                    if self.spreads[market_1_orderbook_bid] is not None
                    and self.spreads[market_2_orderbook_ask] is not None
                    else 0
                )
            elif column == "s6":
                # ask z gieldy 2 vs. bid z gieldy 1
                # sprzedaz do kupna
                self.spreads[self.spreads_column_mapping["s6"]] = (
                    100
                    - (
                        self.spreads[market_2_orderbook_ask]
                        * 100
                        / self.spreads[market_1_orderbook_bid]
                    )
                    if self.spreads[market_2_orderbook_ask] is not None
                    and self.spreads[market_1_orderbook_bid] is not None
                    else 0
                )
            elif column == "s7":
                # bid z gieldy 2 vs. ask z gieldy 1
                self.spreads[self.spreads_column_mapping["s7"]] = (
                    100
                    - (
                        self.spreads[market_2_orderbook_bid]
                        * 100
                        / self.spreads[market_1_orderbook_ask]
                    )
                    if self.spreads[market_2_orderbook_bid] is not None
                    and self.spreads[market_1_orderbook_ask] is not None
                    else 0
                )
            elif column == "s8":
                # ask z gieldy 1 vs. bid z gieldy 2
                self.spreads[self.spreads_column_mapping["s8"]] = (
                    100
                    - (
                        self.spreads[market_1_orderbook_ask]
                        * 100
                        / self.spreads[market_2_orderbook_bid]
                    )
                    if self.spreads[market_1_orderbook_ask] is not None
                    and self.spreads[market_2_orderbook_bid] is not None
                    else 0
                )
            # a teraz liczymy spready dla tickera...
            elif column == "s9":
                # ticker bid z gieldy 1 vs. ticker bid z gieldy 2
                self.spreads[self.spreads_column_mapping["s9"]] = (
                    100 - (
                        self.spreads[market_1_ticker_bid]
                        * 100

                        / self.spreads[market_2_ticker_bid]
                    )
                    if self.spreads[market_1_ticker_bid] is not None
                    and self.spreads[market_2_ticker_bid] is not None
                    else 0
                )
            elif column == "s10":
                # ticker bid z gieldy 2 vs. ticker bid z gieldy 1
                self.spreads[self.spreads_column_mapping["s10"]] = (
                    100 - (
                        self.spreads[market_2_ticker_bid] * 100
                        / self.spreads[market_1_ticker_bid]
                    )
                    if self.spreads[market_2_ticker_bid] is not None
                    and self.spreads[market_1_ticker_bid] is not None
                    else 0
                )
            elif column == "s11":
                # ticker ask z gieldy 1 vs. ticker ask z gieldy 2
                self.spreads[self.spreads_column_mapping["s11"]] = (
                    100 - (
                        self.spreads[market_1_ticker_ask] * 100
                        / self.spreads[market_2_ticker_ask]
                    )
                    if self.spreads[market_1_ticker_ask] is not None
                    and self.spreads[market_2_ticker_ask] is not None
                    else 0
                )
            elif column == "s12":
                # ticker ask z gieldy 2 vs. ticker ask z gieldy 1
                self.spreads[self.spreads_column_mapping["s12"]] = (
                    100 - (
                        self.spreads[market_2_ticker_ask] * 100
                        / self.spreads[market_1_ticker_ask]
                    )
                    if self.spreads[market_2_ticker_ask] is not None
                    and self.spreads[market_1_ticker_ask] is not None
                    else 0
                )
            elif column == "s13":
                # ticker bid z gieldy 1 vs. ticker ask z gieldy 2
                self.spreads[self.spreads_column_mapping["s13"]] = (
                    100 - (
                        self.spreads[market_1_ticker_bid] * 100
                        / self.spreads[market_2_ticker_ask]
                    )
                    if self.spreads[market_1_ticker_bid] is not None
                    and self.spreads[market_2_ticker_ask] is not None
                    else 0
                )
            elif column == "s14":
                # ticker ask z gieldy 2 vs. ticker bid z gieldy 1
                self.spreads[self.spreads_column_mapping["s14"]] = (
                    100 - (
                        self.spreads[market_2_ticker_ask] * 100
                        / self.spreads[market_1_ticker_bid]
                    )
                    if self.spreads[market_2_ticker_ask] is not None
                    and self.spreads[market_1_ticker_bid] is not None
                    else 0
                )
            elif column == "s15":
                # ticker bid z gieldy 2 vs. ticker ask z gieldy 1
                self.spreads[self.spreads_column_mapping["s15"]] = (
                    100 - (
                        self.spreads[market_2_ticker_bid] * 100
                        / self.spreads[market_1_ticker_ask]
                    )
                    if self.spreads[market_2_ticker_bid] is not None
                    and self.spreads[market_1_ticker_ask] is not None
                    else 0
                )
            elif column == "s16":
                # ticker ask z gieldy 1 vs. ticker bid z gieldy 2
                self.spreads[self.spreads_column_mapping["s16"]] = (
                    100 - (
                        self.spreads[market_1_ticker_ask] * 100
                        / self.spreads[market_2_ticker_bid]
                    )
                    if self.spreads[market_1_ticker_ask] is not None
                    and self.spreads[market_2_ticker_bid] is not None
                    else 0
                )
            else:
                raise Exception('wrong spread column')
        logger.debug("spreads: {}".format(self.spreads))

    def get_metrics(self):
        self.metrics = {}
        types = ['orderbook', 'ticker']
        for i, pair in enumerate(self.pairs):
            exchange = self.exchanges[i]
            self.metrics[exchange] = {}
            self.metrics[exchange][pair] = {}
            for type in types:
                self.metrics[exchange][pair][type] = {}
                if type == "orderbook":
                    self.metrics[exchange][pair][type]["mean"] = {
                        "bid": self.orders_buffer[exchange][pair]["p_bid"].mean(),
                        "ask": self.orders_buffer[exchange][pair]["p_ask"].mean()
                    }
                    self.metrics[exchange][pair][type]["std"] = {
                        "bid": self.orders_buffer[exchange][pair]["p_bid"].std(),
                        "ask": self.orders_buffer[exchange][pair]["p_ask"].std()
                    }
                    self.metrics[exchange][pair][type]["min"] = {
                        "bid": self.orders_buffer[exchange][pair]["p_bid"].min(),
                        "ask": self.orders_buffer[exchange][pair]["p_ask"].min()
                    }
                    self.metrics[exchange][pair][type]["max"] = {
                        "bid": self.orders_buffer[exchange][pair]["p_bid"].max(),
                        "ask": self.orders_buffer[exchange][pair]["p_ask"].max()
                    }
                    self.metrics[exchange][pair][type]["shape"] = {
                        "bid": self.orders_buffer[exchange][pair]["p_bid"].shape(),
                        "ask": self.orders_buffer[exchange][pair]["p_ask"].shape()
                    }
                elif type == "ticker":
                    self.metrics[exchange][pair][type]["mean"] = {
                        "bid": self.tickers_buffer[exchange][pair]["b"].mean(),
                        "ask": self.tickers_buffer[exchange][pair]["a"].mean()
                    }
                    self.metrics[exchange][pair][type]["std"] = {
                        "bid": self.tickers_buffer[exchange][pair]["b"].std(),
                        "ask": self.tickers_buffer[exchange][pair]["a"].std()
                    }
                    self.metrics[exchange][pair][type]["min"] = {
                        "bid": self.tickers_buffer[exchange][pair]["b"].min(),
                        "ask": self.tickers_buffer[exchange][pair]["a"].min()
                    }
                    self.metrics[exchange][pair][type]["max"] = {
                        "bid": self.tickers_buffer[exchange][pair]["b"].max(),
                        "ask": self.tickers_buffer[exchange][pair]["a"].max()
                    }
                    self.metrics[exchange][pair][type]["shape"] = {
                        "bid": self.tickers_buffer[exchange][pair]["b"].shape(),
                        "ask": self.tickers_buffer[exchange][pair]["a"].shape()
                    }
                else:
                    raise Exception("Unknown type.")
        orderbooks_bid = pd.concat([
            self.orders_buffer[self.exchanges[0]][self.pairs[0]]["p_bid"],
            self.orders_buffer[self.exchanges[1]][self.pairs[1]]["p_bid"]
        ]).sort_index()
        orderbooks_ask = pd.concat([
            self.orders_buffer[self.exchanges[0]][self.pairs[0]]["p_ask"],
            self.orders_buffer[self.exchanges[1]][self.pairs[1]]["p_ask"]
        ]).sort_index()
        self.metrics["orderbooks"]["std"] = {
            "bid": orderbooks_bid.std(),
            "ask": orderbooks_ask.std()
        }
        self.metrics["orderbooks"]["mean"] = {
            "bid": orderbooks_bid.mean(),
            "ask": orderbooks_ask.mean()
        }

    def filter_orders(self):
        if len(self.orders_buffer) < 1 or len(self.tickers_buffer) < 1:
            raise Exception("buffer to small")
        elif len(self.orders_buffer) == 2 and len(self.tickers_buffer) == 2:
            # aby entry w orderbooku dla danej gieldy byl wazny musi miec niezerowy
            # price oraz quantity, reszta odpada.
            # jesli order ma dodatni price a zerowy quantity to jest fake

            self.orders_buffer[0] = self.orders_buffer[0][
                (
                    (
                        (self.orders_buffer[0]["p_bid"] > 0)
                        & (self.orders_buffer[0]["q_bid"] > 0)
                    )
                    | (
                        (self.orders_buffer[0]["p_ask"] > 0)
                        & (self.orders_buffer[0]["q_ask"] > 0)
                    )
                )
            ]
            self.orders_buffer[1] = self.orders_buffer[1][
                (
                    (
                        (self.orders_buffer[1]["p_bid"] > 0)
                        & (self.orders_buffer[1]["q_bid"] > 0)
                    )
                    | (
                        (self.orders_buffer[1]["p_ask"] > 0)
                        & (self.orders_buffer[1]["q_ask"] > 0)
                    )
                )
            ]
        else:
            raise Exception("Not supported bufer size.")

    def process_buffer(self):
        if len(self.orders_buffer) < 1 or len(self.tickers_buffer) < 1:
            raise Exception("buffer to small")
        elif len(self.orders_buffer) == 2 and len(self.tickers_buffer) == 2:
            self.orders = (
                self.orders_buffer[self.exchanges[0]][self.pairs[0]]
                .join(
                    self.orders_buffer[self.exchanges[1]][self.pairs[1]],
                    how="outer",
                    lsuffix=self.suffixes["l"],
                    rsuffix=self.suffixes["r"],
                )
                .sort_index()
                .bfill()
                .ffill()
            )
            # self.orders_buffer = None
            self.tickers = (
                self.tickers_buffer[self.exchanges[0]][self.pairs[0]]
                .join(
                    self.tickers_buffer[self.exchanges[1]][self.pairs[1]],
                    how="outer",
                    lsuffix=self.suffixes["l"],
                    rsuffix=self.suffixes["r"],
                )
                .sort_index()
                .bfill()
                .ffill()
            )
            # self.tickers_buffer = None
        else:
            raise Exception("Not supported bufer size.")

    def put_spreads(self):
        try:
            return self.writer.write_dataframe(
                spreads=self.spreads,
                exchanges=self.exchanges,
                pairs=self.pairs,
                column_mapping=helper.reverse_dict(self.spreads_column_mapping),
            )
        except Exception as e:
            logger.warning("put_spreads ex {}".format(e))

    # def get_signals(self):
    #     signals = pd.DataFrame()
    #     for column in self.spreads_default_columns:
    #         threshold = SPREAD_THRESHOLDS[self.market_type.upper()][column]
    #         spread = self.spreads_column_mapping[column]
    #         if threshold is not None:
    #             # result = self.spreads[(self.spreads[spread] > 0)]
    #             # query = "`{}`{}".format(spread, threshold)
    #             filter = (
    #                 self.spreads[spread] > threshold
    #                 if
    #             )
    #             logger.debug("query {}".format(query))
    #             result = self.spreads.query(query)
    #             logger.debug("result {}".format(result))
    #             if len(result) > 0:
    #                 signals = signals.append(result)
    #                 logger.info("Found signals {} with {} valued:
    # {}{}".format(len(signals), column, spread, threshold))
    #                 logger.debug(result)
    #         else:
    #             raise Exception('threshold is not definied')
    #     if len(signals) > 0:
    #         logger.info("Found {} signals from {} entries".format(len(signals), len(self.spreads)))
    #         # self.spreads = signals.sort_index()
    #     else:
    #         logger.info("No signals")

    def run_forever(self):
        while True:
            try:
                self.get_orderbooks()
                self.get_tickers()
                self.get_metrics()
                self.filter_orders()
                self.process_buffer()
                self.get_spreads()
                self.get_signals()
                # self.put_spreads()
                time.sleep(SPREAD_WRITE_INTERVAL)
            except Exception as e:
                logger.warning("run forever ex {}".format(e))
                return

    @property
    def status(self):
        try:
            return self._t._running
        except Exception:
            return False

    def start(self):
        self._t = Thread(target=self.run_forever)
        self._t.daemon = True
        self._t._running = True
        self._t.start()
        logger.info(SPREAD_STARTED)

    def stop(self):
        self._t._running = False
        self._t.join()
        logger.info(SPREAD_STOPPED)

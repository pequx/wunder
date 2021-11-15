import collections
import json
import logging
import websocket

from decimal import Decimal
from multiprocessing.dummy import Process as Thread

from hundi.config.message import (
    CHANNEL_SUBSCRIPTION_STATUS,
    CHANNEL_SYSTEM_STATUS,
    CONTRACT_SUBSCRIPTION_STATUS,
    SNAPSHOT_MESSAGE,
    SUBSCRIBED_TO_CHANNELS,
    UNCLASSIFIED_MESSAGE,
    UNKNOWN_MARKET_TYPE,
    WEBSCOKED_STARTED,
    WEBSOCKET_CLOSED,
    WEBSOCKET_ERROR,
    WEBSOCKET_EXCEPTION_ON_CLOSE,
    WEBSOCKET_STOPPED,
)
from hundi.config.market import (
    MARKET_KRAKEN_NAME,
    MARKET_KRAKEN_WEBSOCKET_URL,
)
from hundi.config.ticker import (
    TICKER_COLUMNS,
    TICKER_OHLC_COLUMNS,
)
from hundi.model.ticker import TickerFutures, TickerSpot
from hundi.writer.ticker import KairosDBTickerWriter as Writer

logger = logging.getLogger(__name__)


class WebsocketTicker(object):
    def __init__(self, writer: Writer, market_type: str, pairs: str, interval):
        self.writer = writer
        self.writer.exchange = (
            MARKET_KRAKEN_NAME["SPOT"]
            if market_type == "spot"
            else MARKET_KRAKEN_NAME["FUTURES"]
        )
        self.writer.market_type = market_type
        self.pairs = pairs
        self.interval = int(interval)
        self.tick = {}
        self.topic_pair = {}
        self.channels = {}
        self.market_type = market_type

        self._ws = websocket.WebSocketApp(
            MARKET_KRAKEN_WEBSOCKET_URL["SPOT"]
            if market_type == "spot"
            else MARKET_KRAKEN_WEBSOCKET_URL["FUTURES"],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, message: str):
        message = json.loads(message)

        if self.market_type == "spot":
            if "event" in message:
                if message.get("event") == "systemStatus":
                    logger.info(
                        CHANNEL_SYSTEM_STATUS.format(
                            message.get("status", "unknown"),
                            message.get("version", "unknown"),
                        )
                    )
                if message.get("event") == "subscriptionStatus":
                    if message.get("errorMessage"):
                        logger.error(message["errorMessage"])
                        return
                    logger.info(
                        CHANNEL_SUBSCRIPTION_STATUS.format(
                            message["status"], message["channelID"], message["pair"]
                        )
                    )
                    self.channels[message["channelID"]] = {
                        "pair": message["pair"],
                        "status": message["status"],
                    }
            elif message[3] is not None:
                logger.debug(SNAPSHOT_MESSAGE.format(message))
                key = message[3]
                # candle = self.get_candle(message)
                ticker = self.get_ticker(message)
                self.writer.write(key, ticker, self.interval)
                # self.writer.write(key, candle)

            else:
                logger.warning(UNCLASSIFIED_MESSAGE.format(message))
        elif self.market_type == "futures":
            if "event" in message:
                if message.get("event") == "info":
                    logger.info(
                        CHANNEL_SYSTEM_STATUS.format(
                            message.get("event", "unknown"),
                            message.get("version", "unknown"),
                        )
                    )
                if message.get("event") == "subscribed":
                    logger.info(
                        CONTRACT_SUBSCRIPTION_STATUS.format(
                            message.get("event"), message.get("product_ids")
                        )
                    )
                    for product_id in message.get("product_ids"):
                        self.channels[product_id] = {"status": message.get("event")}
            elif "feed" in message:
                if message.get("feed") == "ticker":
                    logger.debug(SNAPSHOT_MESSAGE.format(message))
                    key = message["product_id"]
                    ticker = self.get_ticker(message)
                    self.writer.write(key, ticker)
            else:
                logger.warning(UNCLASSIFIED_MESSAGE.format(message))
        else:
            logger.warning(UNKNOWN_MARKET_TYPE.format(self.market_type))

    def get_snapshots(self):
        return None

    def get_ticker(self, message):
        if self.market_type == "futures":
            ticker = TickerFutures(
                timestamp=float(message["time"] / 1000),
                bid=Decimal(message["bid"]),
                ask=Decimal(message["ask"]),
                bid_size=Decimal(message["bid_size"]),
                ask_size=Decimal(message["ask_size"]),
                volume=Decimal(message["volume"]),
            )
            return ticker
        elif self.market_type == "spot":
            DataTicker = collections.namedtuple("Data", TICKER_COLUMNS["SPOT"])
            msg = DataTicker._make(message)
            if msg.channelName.startswith("ohlc"):
                DataOHLC = collections.namedtuple("OHLC", TICKER_OHLC_COLUMNS["SPOT"])
                ohlc = DataOHLC._make(msg.points)
                ticker = TickerSpot(
                    timestamp=float(ohlc.etime),
                    open=Decimal(ohlc.open),
                    high=Decimal(ohlc.high),
                    low=Decimal(ohlc.low),
                    close=Decimal(ohlc.close),
                    volume=Decimal(ohlc.volume),
                )
                return ticker
        else:
            logger.warning(UNKNOWN_MARKET_TYPE.format(self.market_type))

    # def get_candle(self, message):
    #     if self.market_type == "spot":
    #         msg = Data._make(message)
    #         if msg.channelName.startswith("ohlc"):
    #             ohlc = DataOHLC._make(msg.points)
    #             candle = Candle(
    #                 timestamp=int(Decimal(ohlc.etime))
    #                 - 60 * MARKET_KRAKEN_INTERVAL["SPOT"],
    #                 period=CandlePeriod(MARKET_KRAKEN_INTERVAL["SPOT"] * 60),
    #                 open=Decimal(ohlc.open),
    #                 high=Decimal(ohlc.high),
    #                 low=Decimal(ohlc.low),
    #                 close=Decimal(ohlc.close),
    #                 volume=Decimal(ohlc.volume),
    #             )
    #             return candle
    #         else:
    #             logger.warning(UNKNOWN_CANDLE_DATA_TYPE.format(msg))
    # elif self.market_type == "futures":
    #     candle = Candle(
    #         timestamp=int(message["time"] / 1000),
    #         period=CandlePeriod(MARKET_KRAKEN_INTERVAL["FUTURES"] * 60),
    #         high=Decimal(message["bid"]),
    #         low=Decimal(message["ask"]),
    #         open=Decimal(message["markPrice"]),
    #         close=Decimal(message["last"]),
    #         volume=Decimal(message["volume"]),
    #     )
    #     return candle
    # else:
    #     logger.warning(UNKNOWN_MARKET_TYPE.format(self.market_type))
    # logger.debug(candle)

    def on_error(self, error):
        logger.error(WEBSOCKET_ERROR.format(repr(error)))
        self.stop()
        self.start()

    def on_close(self):
        if self._t._running:
            try:
                self.stop()
            # except Exception as e:
            #     logger.exception(e)
            # try:
            #     self.start()
            except Exception as e:
                logger.error(WEBSOCKET_EXCEPTION_ON_CLOSE)
                logger.exception(e)
                # self.stop()
        else:
            logger.info(WEBSOCKET_CLOSED)

    def on_open(self):
        if self.market_type == "spot":
            subscribe = json.dumps(
                {
                    "event": "subscribe",
                    "pair": self.pairs,
                    "subscription": {
                        "name": "ohlc",
                        "interval": self.interval,
                    },
                }
            )
        elif self.market_type == "futures":
            subscribe = json.dumps(
                {
                    "event": "subscribe",
                    "feed": "ticker",
                    "product_ids": self.pairs,
                }
            )
        else:
            logger.warning(UNKNOWN_MARKET_TYPE.format(self.market_type))
            return
        logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))
        self._ws.send(subscribe)
        return

    @property
    def status(self):
        """
        Returns True if the websocket is running, False if not
        """
        try:
            return self._t._running
        except Exception:
            return False

    def start(self):
        """ Run the websocket in a thread """
        self._t = Thread(target=self._ws.run_forever)
        self._t.daemon = True
        self._t._running = True
        self._t.start()
        logger.info(WEBSCOKED_STARTED)

    def stop(self):
        """ Stop/join the websocket thread """
        self._t._running = False
        self._ws.close()
        self._t.join()
        logger.info(WEBSOCKET_STOPPED)


# Message examples from Kraken:
#

# {'connectionID': 16717317552560144119,
#  'event': 'systemStatus',
#  'status': 'online',
#  'version': '1.6.0'}

# {'channelID': 328,
#  'channelName': 'ohlc-5',
#  'event': 'subscriptionStatus',
#  'pair': 'XBT/USD',
#  'status': 'subscribed',
#  'subscription': {'interval': 5, 'name': 'ohlc'}}

# [328,
#  ['1609094877.487963',
#   '1609095000.000000',
#   '26795.70000',
#   '26807.00000',
#   '26763.50000',
#   '26790.50000',
#   '26786.96397',
#   '40.34901118',
#   144],
#  'ohlc-5',
#  'XBT/USD']

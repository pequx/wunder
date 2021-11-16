import json
import logging
import requests
import websocket

from decimal import Decimal
from multiprocessing import Process
from queue import Queue

from config.message import (
    CONTRACT_SUBSCRIPTION_STATUS,
    SNAPSHOT_MESSAGE,
    SUBSCRIBED_TO_CHANNELS,
    UNKNOWN_MARKET_TYPE,
    WEBSCOKED_STARTED,
    WEBSOCKET_CLOSED,
    WEBSOCKET_ERROR,
    WEBSOCKET_EXCEPTION_ON_CLOSE,
    WEBSOCKET_STOPPED,
    UNKNOWN_PAIRS
)
from config.market import (
    MARKET_FTX_NAME,
    MARKET_FTX_WEBSOCKET_URL,
)
from model.ticker import TickerFutures as TickerFTX
from writer.ticker import KairosDBTickerWriter as Writer
from lib import helper

logger = logging.getLogger(__name__)


class TickerFtxCryptoController(Process):
    def __init__(self, writer: Writer, market_type: str, pair: str):
        self.writer = writer
        self.market_type = market_type.lower()
        self.pair = pair.lower()
        self.exchange = MARKET_FTX_NAME["spot"] if self.market_type == "spot" else MARKET_FTX_NAME["futures"],
        self.channels = {}
        self.volumes = {}
        self.message = {}
        self.ticker = {}
        self._ws = websocket.WebSocketApp(
            MARKET_FTX_WEBSOCKET_URL["spot"] if self.market_type == "spot" else MARKET_FTX_WEBSOCKET_URL["futures"],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_open(self):
        if self.market_type == "spot" or self.market_type == "futures":
            subscribe = json.dumps(
                {"op": "subscribe", "channel": "ticker", "market": self.pair.upper()}
            )
            logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))
            self._ws.send(subscribe)
        else:
            return Exception(UNKNOWN_MARKET_TYPE.format(self.market_type))

    def on_message(self, message: str):
        self.message = json.loads(message)

        if "type" in message:
            type = self.message.get("type")
            pair = self.message.get("market").lower()

            if type == "subscribed":
                logger.info(CONTRACT_SUBSCRIPTION_STATUS.format(type, pair))
                # if self.get_volumes() is False:
                #     logger.warning("No volumes.")
                self.channels[pair] = {"status": type}
            elif type == "update":
                logger.debug(SNAPSHOT_MESSAGE.format(message))

                if pair != self.pair:
                    return Exception('Pairs do not match.')

                if self.get_ticker() is False:
                    return Exception('No ticker')

                if self.writer.write(
                        path=helper.get_metric_name(type="crypto", exchange=self.exchange, key=pair),
                        ticker=self.ticker) is False:
                    logger.error("Write error")
                self.ticker = {}
        else:
            return Exception("missing Market type")

    def on_error(self, e):
        logger.error(WEBSOCKET_ERROR.format(repr(e)))

        self.stop()

    def on_close(self):
        if self._t._running:
            self.stop()
            logger.info(WEBSOCKET_CLOSED)

    # def get_volumes(self):
    #     url = "{}{}".format(
    #         MARKET_FTX_REST_URL[self.market_type]["snapshot"],
    #         self.pair.replace("/", "%2F"),
    #     )
    #     logger.debug(url)
    #     response = requests.get(url).json()
    #     # if response.get("success") is False:
    #     #     logger.warning("no volume.")
    #     logger.debug(response)
    #     result = response["result"]
    #     self.volumes[self.pair] = (
    #         Decimal(result["volume"])
    #         if self.market_type == "futures"
    #         else Decimal(result["quoteVolume24h"])
    #     )
    #     logger.debug(self.volumes)
    #     if len(self.volumes) == len(self.pairs):
    #         return True
    #     else:
    #         return False

    def get_ticker(self):
        try:
            data = self.message.get("data")
            if data is None:
                return Exception("No data")

            bid_size = Decimal(data.get("bidSize"))
            ask_size = Decimal(data("ask_size"))
            # self.volumes[message["market"]] += bid_size + ask_size

            self.ticker = TickerFTX(
                timestamp=float(data["time"]),  # to float unix
                bid=Decimal(data["bid"]),
                ask=Decimal(data["ask"]),
                bid_size=bid_size,
                ask_size=ask_size,
                volume=0,
            )

            return True
        except Exception as e:
            logger.exception(e)

            return False

    @property
    def status(self):
        try:
            return self._t._running
        except Exception:
            return False

    def start(self):
        self._t = Process(target=self._ws.run_forever)
        self._t.daemon = True
        self._t._running = True
        self._t.start()
        logger.info(WEBSCOKED_STARTED)

    def stop(self):
        self._t._running = False
        self._ws.close()
        self._t.join()
        logger.info(WEBSOCKET_STOPPED)

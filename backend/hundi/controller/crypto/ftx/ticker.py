import json
import logging
from decimal import Decimal
from multiprocessing.dummy import Process as Thread

import requests
import websocket

from hundi.config.message import (
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
from hundi.config.market import (
    MARKET_FTX_NAME,
    MARKET_FTX_REST_URL,
    MARKET_FTX_WEBSOCKET_URL,
)
from hundi.model.ticker import TickerFutures as TickerFTX
from hundi.writer.ticker import Kai

logger = logging.getLogger(__name__)


class WebsocketTicker(Thread):
    def __init__(self, writer, market_type, pairs):
        self.writer = writer
        self.writer.exchange = (
            MARKET_FTX_NAME["SPOT"]
            if market_type == "spot"
            else MARKET_FTX_NAME["FUTURES"]
        )
        self.writer.market_type = market_type
        self.pairs = pairs
        self.tick = {}
        self.topic_pair = {}
        self.channels = {}
        self.market_type = market_type
        self.volumes = {}

        self._ws = websocket.WebSocketApp(
            MARKET_FTX_WEBSOCKET_URL["SPOT"]
            if market_type == "spot"
            else MARKET_FTX_WEBSOCKET_URL["FUTURES"],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_message(self, message):
        message = json.loads(message)
        if "type" in message:
            if message.get("type") == "subscribed":
                logger.debug(
                    CONTRACT_SUBSCRIPTION_STATUS.format(
                        message.get("type"), message.get("market")
                    )
                )
                if self.get_volumes() is False:
                    logger.warning("No volumes.")
                self.channels[message.get("market")] = {"status": message.get("type")}
            elif message.get("type") == "update":
                logger.debug(SNAPSHOT_MESSAGE.format(message))
                key = message["market"]
                ticker = self.get_ticker(message)
                self.writer.write(key, ticker)

    def get_volumes(self):
        for pair in self.pairs:
            url = "{}{}".format(
                MARKET_FTX_REST_URL[self.market_type.upper()]["SNAPSHOT"],
                pair.upper().replace("/", "%2F"),
            )
            logger.debug(url)
            response = requests.get(url).json()
            # if response.get("success") is False:
            #     logger.warning("no volume.")
            logger.debug(response)
            result = response["result"]
            self.volumes[pair.upper()] = (
                Decimal(result["volume"])
                if self.market_type == "futures"
                else Decimal(result["quoteVolume24h"])
            )
        logger.debug(self.volumes)
        if len(self.volumes) == len(self.pairs):
            return True
        else:
            return False

    def get_ticker(self, message):
        data = message.get("data")
        logger.debug(message)
        bid_size = Decimal(data["bidSize"])
        ask_size = Decimal(data["askSize"])
        self.volumes[message["market"]] += bid_size + ask_size
        ticker = TickerFTX(
            timestamp=float(data["time"]),  # to float unix
            bid=Decimal(data["bid"]),
            ask=Decimal(data["ask"]),
            bid_size=bid_size,
            ask_size=ask_size,
            volume=self.volumes[message["market"]],
        )
        return ticker

    def on_error(self, error):
        logger.error(WEBSOCKET_ERROR.format(repr(error)))
        self.stop()

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
        if self.pairs is None:
            logger.warning(UNKNOWN_PAIRS.format(self.paris))
            subscribe = json.dumps(
                {"op": "subscribe", "channel": "markets"}
            )
            logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))
            self._ws.send(subscribe)
        else:
            if self.market_type == "spot" or self.market_type == "futures":
                for pair in self.pairs:
                    subscribe = json.dumps(
                        {"op": "subscribe", "channel": "ticker", "market": pair}
                    )
                    logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))
                    self._ws.send(subscribe)
            else:
                logger.warning(UNKNOWN_MARKET_TYPE.format(self.market_type))
                return
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

import logging
import json

from abc import ABC, abstractmethod
from decimal import Decimal
from websocket import WebSocketApp

from hundi.lib.executor import ExecutorLib as Executor
from hundi.writer.ticker import KairosDBTickerWriter as Writer
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
    MARKET_FTX_WEBSOCKET_URL,
)
from hundi.config.ticker import TICKER_ACTION
from hundi.lib import helper
from hundi.model.ticker import TickerFutures as TickerFTX

logger = logging.getLogger(__name__)


class TickerFtxCryptoAction(ABC):
    def __init__(self, market_type: str, pair: str):
        self.executor = Executor()
        self.writer = Writer()
        self.market_type = market_type.lower()
        self.pair = pair.lower()
        self.exchange = MARKET_FTX_NAME["spot"] if self.market_type == "spot" else MARKET_FTX_NAME["futures"]
        self.buffer = None
        self.ticker = None
        self._ws = WebSocketApp(
            url=MARKET_FTX_WEBSOCKET_URL["spot"] if self.market_type == "spot" else MARKET_FTX_WEBSOCKET_URL["futures"],
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )

    def on_open(self) -> None:
        if self.market_type == "spot" or self.market_type == "futures":
            subscribe = json.dumps(
                {"op": "subscribe", "channel": "ticker", "market": self.pair.upper()}
            )
            logger.info(SUBSCRIBED_TO_CHANNELS.format(subscribe))

            self._ws.send(subscribe)
        else:
            raise RuntimeError(UNKNOWN_MARKET_TYPE.format(self.market_type))

    def on_message(self, message: str) -> None:
        if self.buffer is None:
            self.buffer = json.loads(message)

            if len(self.buffer) > 0:
                if "type" in message:
                    type = self.message.get("type")
                    pair = self.message.get("market").lower()

                    if type == "subscribed":
                        logger.info(CONTRACT_SUBSCRIPTION_STATUS.format(type, pair))
                        self.channels[pair] = {"status": type}
                    elif type == "update":
                        logger.debug(SNAPSHOT_MESSAGE.format(message))

                        if pair != self.pair:
                            raise Exception('Pairs do not match.')

                        if self.get_ticker() is False:
                            raise Exception('No ticker')

                        if self.writer.write(
                                path=helper.get_metric_name(type="crypto", exchange=self.exchange, key=pair),
                                ticker=self.ticker) is False:
                            raise Exception("write error")
                        self.buffer = None
                        self.ticker = None
                else:
                    raise Exception("missing Market type")
            else:
                raise Exception("no message.")
        else:
            raise Exception("Message buffer not empty.")

    def on_error(self, e) -> None:
        logger.error(WEBSOCKET_ERROR.format(repr(e)))

        self.executor.cancel()

    def on_close(self) -> None:
        if self.executor.busy:
            self.executor.cancel()

            logger.info(WEBSOCKET_CLOSED)

    def get_ticker(self) -> bool:
        try:
            data = self.buffer.get("data")
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

    @abstractmethod
    def start(self):
        try:
            self.executor.try_run_async(TICKER_ACTION, self._ws.run_forever)
        except Exception or RuntimeError as e:
            logger.exception(e)
            return e

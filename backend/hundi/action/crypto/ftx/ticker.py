import logging
import json
from click.decorators import make_pass_decorator
import websocket

from typing import Any, Dict, List
from decimal import Decimal
from threading import Thread

from hundi.writer.ticker import KairosDBTickerWriter
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
    MARKET_FTX_CHANNEL,
    MARKET_FTX_SUBSCRIPTION,
    MARKET_FTX_WEBSOCKET_URL,
)
from hundi.lib import helper
from hundi.model.ticker import TickerFutures as TickerFTX

logger = logging.getLogger(__name__)


class TickerFtxCryptoAction(object):
    def __init__(self, paths: object):
        try:
            self.paths = paths
            self.url = helper.get_url(paths)
            self.header = None
            self._buffer = None
            self.channel = MARKET_FTX_CHANNEL
            self._thread = Thread(target=self.start, name=__name__)
            self._ws = websocket.WebSocketApp(
                self.url,
                self.header,
                self.on_open,
                self.on_message,
                self.on_error,
                self.on_close
            )
            self.markets_only = False
            if helper.get_subscription(paths) == "markets":
                self.markets_only = True
            else:
                self.writer = KairosDBTickerWriter(self.paths)
            self.lock = True
        except Exception as e:
            logger.exception(e)
            return

    def start(self):
        try:
            logger.info("Starting thread {}".format(__name__))
            if not self.markets_only:
                self.writer.start()
            self.lock = False
            self._ws.run_forever(ping_interval=15, ping_timeout=5)
        except Exception as e:
            logger.exception(e)
            self.lock = True
            self.stop()

    def stop(self) -> None:
        try:
            logger.info("Stopping websocket...")
            if not self.markets_only:
                if self.writer.is_alive:
                    self.writer.stop()
            self.lock = True
            # if self._thread.is_alive:
            #     self._thread.join(1)
            self._ws.close()
        except Exception as e:
            logger.exception(e)
            self.lock = True

    def on_error(self, ws: websocket.WebSocket, error: Any) -> None:
        if error.__doc__ == "Program interrupted by user.":
            logger.info(error.__doc__)
        else:
            logger.error("Websocket error".format(repr(error)))

        self.stop()

    def on_close(self, ws: websocket.WebSocket, status_code, message) -> None:
        try:
            logger.info("Closing websocket {} {}".format(status_code, message))
        except Exception as e:
            logger.exception(e)

    def on_open(self, ws: websocket.WebSocket) -> None:
        try:
            if "subscribed" not in self.channel['markets']:
                ws.send(json.dumps(MARKET_FTX_SUBSCRIPTION['markets']))
        except Exception as e:
            logger.exception(e)
            self.stop()

    def on_message(self, ws: websocket.WebSocket, message: str) -> None:
        try:
            if self._buffer is None:
                self._buffer = json.loads(message)

                if len(self._buffer) > 0:
                    logger.debug("Processing message: {}".format(self._buffer))

                    if "type" in self._buffer:
                        type = self._buffer.get("type")
                        channel = self._buffer.get('channel')
                        market = self._buffer.get('market')

                        if type == "subscribed":
                            if channel == 'markets':
                                self.channel['markets'] = {"subscribed": True}
                            elif channel == 'ticker':
                                name = helper.format_name(market)
                                self.channel['ticker'][name] = {"subscribed": True}
                            else:
                                raise Exception('unknown channel.')
                            logger.debug("Subscribed channels: {}".format(self.channel))
                        elif type == "partial":
                            if channel == 'markets':
                                markets = self.match_markets() if not self.markets_only else self.get_markets()

                                if not self.markets_only:
                                    for name in markets:
                                        if name not in self.channel['ticker']:
                                            subscription = MARKET_FTX_SUBSCRIPTION['ticker']
                                            subscription['market'] = markets[name]['name'].upper()

                                            ws.send(json.dumps(subscription))
                                            logger.debug("Send subscription: {}".format(subscription))
                                else:
                                    logger.info("Markets: {}".format(markets))
                                    self.stop()
                        elif type == "update":
                            if channel == 'ticker':
                                name = helper.format_name(market)
                                if not self.channel['ticker'].get(name).get('subscribed'):
                                    raise Exception('Invalid update')
                                elif not self.writer:
                                    raise Exception("No writer.")
                                elif self.writer.lock:
                                    raise Exception("Writer lock present")

                                ticker = self.get_ticker()
                                # path = self.paths[name]

                                logger.debug("Writing ticker: {} {}".format(name, ticker.timestamp))
                                self.writer.put(name, ticker)
                            else:
                                raise Exception('unknown channel/market.')
                    else:
                        raise Exception("Unknown message type.")
                else:
                    raise Exception("No message in _buffer.")
            else:
                raise Exception("Message _buffer not empty.")
        except Exception as e:
            logger.exception(e)
            self.stop()
        finally:
            self._buffer = None

    def get_markets(self) -> Dict:
        try:
            data = self._buffer.get("data").get("data")
            if not data:
                raise Exception("No data")
            return data
        except Exception as e:
            logger.exception(e)
            self.stop()

    def match_markets(self) -> Dict:
        try:
            data = self._buffer.get("data").get("data")
            if not data:
                raise Exception("No data")
            markets = {}
            for name in self.paths:
                path = self.paths[name]
                market = path['market']
                if market == "markets":
                    pass
                match = data[market.upper()]
                if len(match) < 1:
                    raise Exception("No market description.")
                markets[name] = match
                logger.debug('Updated markets: {}'.format(markets))
            return markets
        except Exception as e:
            logger.exception(e)
            self.stop()

    def get_ticker(self) -> TickerFTX:
        try:
            data = self._buffer.get("data")
            if data is None:
                return Exception("No data")

            bid_size = Decimal(data.get("bidSize"))
            ask_size = Decimal(data.get('askSize'))
            # self.volumes[message["market"]] += bid_size + ask_size

            ticker = TickerFTX(
                timestamp=float(data["time"]),  # to float unix
                bid=Decimal(data.get("bid")),
                ask=Decimal(data.get("ask")),
                bid_size=bid_size,
                ask_size=ask_size,
                volume=0,
            )
            return ticker
        except Exception as e:
            logger.exception(e)
            self.stop()

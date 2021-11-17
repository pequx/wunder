import time
import logging

from hundi.writer.ticker import KairosDBTickerWriter as Writer
from hundi.controller.crypto.ftx.ticker import TickerFtxCryptoController as Controller
from hundi.config.market import MARKET_FTX_NAME

logger = logging.getLogger(__name__)


class TickerFtxCryptoAction(object):
    def __init__(self, market_type: str, pair: str):
        self.writer = Writer()
        self.controller = Controller(self.writer, market_type, pair)

    def start(self):
        try:
            self.controller.start()
            while True:
                time.sleep(5)
        except Exception as e:
            logger.exception(e)
            return e

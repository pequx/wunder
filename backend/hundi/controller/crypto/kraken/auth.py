import base64
import hashlib
import hmac
import logging
import time
import urllib.request
from multiprocessing.dummy import Process as Thread

from hundi.config.message import (
    AUTH_STARTED,
    AUTH_STOPPED,
)
from hundi.config.market import (
    MARKET_KRAKEN_API_KEY,
    MARKET_KRAKEN_API_SIGN,
    MARKET_KRAKEN_TOKEN_PATH,
    MARKET_KRAKEN_TOKEN_URL,
)

logger = logging.getLogger(__name__)


class ApiAuth(object):
    def __init__(self):
        try:
            self.token = ""
            self.is_running = False
            self._t = Thread(target=self.get_token)
        except Exception as e:
            logger.error("Init exception {}".format(e))

    def get_token(self):
        try:
            nonce = bytes(str(int(time.time() * 1000)), "utf-8")
            sign = base64.b64encode(
                hmac.new(
                    base64.b64decode(MARKET_KRAKEN_API_SIGN),
                    MARKET_KRAKEN_TOKEN_PATH
                    + hashlib.sha256(nonce + b"nonce=%s" % nonce).digest(),
                    hashlib.sha512,
                ).digest()
            )
            # headers = {
            #     "API-Key": MARKET_KRAKEN_API_KEY,
            #     "API-Sign": sign.decode('utf-8')
            # }
            # logger.debug(headers)
            logger.debug(nonce)
            logger.debug(sign)
            api_request = urllib.request.Request(
                MARKET_KRAKEN_TOKEN_URL, b"nonce=%s" % nonce
            )
            logger.debug(api_request)
            # api_request = requests
            api_request.add_header("API-Key", MARKET_KRAKEN_API_KEY)
            api_request.add_header("API-Sign", sign)
            # r = requests.get(url=MARKET_KRAKEN_TOKEN_URL, headers=headers)
            # logger.debug(r)
            response = urllib.request.urlopen(api_request).read()
            logger.info(response)
            # with urlopen(api_request) as response:
            #    test = response.read()
            #    trololoo
            # logger.info(test)

            # self.token = json.loads()["result"][
            #     "token"
            # ]
            # if len(self.token) > 1:
            #     logger.info(AUTH_TOKEN_ACQUIRED.format(MARKET_KRAKEN_TOKEN_URL))
            # else:
            #     logger.warning(AUTH_TOKEN_SIZE.format(MARKET_KRAKEN_TOKEN_URL))
        except Exception as e:
            logger.warning("run forever ex {}".format(e))

    @property
    def status(self):
        try:
            return self._t._running
        except Exception:
            return False

    def start(self):
        self._t.daemon = True
        self._t._running = True
        self._t.start()
        logger.info(AUTH_STARTED.format(MARKET_KRAKEN_TOKEN_URL))

    def stop(self):
        self._t._running = False
        self._t.join()
        logger.info(AUTH_STOPPED)

from unittest import TestCase, main
from unittest.mock import MagicMock

from hundi.controller.crypto.ftx.ticker import TickerFtxCryptoController
from hundi.writer.ticker import KairosDBTickerWriter
from lib.kairosdb.ticker import TickerKairosDbLib


class TickerFtxCryptoControllerUnitTest(TestCase):
    def setUp(self) -> None:
        db = MagicMock()
        writer = MagicMock(db)

        self.controller = TickerFtxCryptoController(writer, market_type="")
        return super().setUp()

    def test_always_passes(self):
        self.assertTrue(True)


if __name__ == '__main__':
    main()

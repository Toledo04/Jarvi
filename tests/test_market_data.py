import unittest
from unittest.mock import patch

import httpx

from market_data import (
    AlpacaCredentialsError,
    MarketDataUnavailable,
    StockTradeNotFound,
    get_latest_stock_trade,
)


class FakeResponse:
    def __init__(self, payload: object, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://example.test/trade")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError(
                "fake Alpaca error", request=request, response=response
            )

    def json(self) -> object:
        return self.payload


class GetLatestStockTradeTests(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {"APCA_API_KEY_ID": "test-key", "APCA_API_SECRET_KEY": "test-secret"},
    )
    @patch("market_data.httpx.get")
    def test_returns_normalized_trade(self, mock_get) -> None:
        mock_get.return_value = FakeResponse(
            {"trade": {"p": 184.25, "t": "2026-10-27T15:30:00Z"}}
        )

        result = get_latest_stock_trade("AAPL")

        self.assertEqual(
            result,
            {
                "symbol": "AAPL",
                "price": 184.25,
                "timestamp": "2026-10-27T15:30:00Z",
                "source": "Alpaca IEX latest trade",
            },
        )
        self.assertEqual(mock_get.call_args.kwargs["params"], {"feed": "iex"})

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_credentials_raise_clear_error(self) -> None:
        with self.assertRaises(AlpacaCredentialsError):
            get_latest_stock_trade("AAPL")

    @patch.dict(
        "os.environ",
        {"APCA_API_KEY_ID": "test-key", "APCA_API_SECRET_KEY": "test-secret"},
    )
    @patch("market_data.httpx.get")
    def test_not_found_response_maps_to_domain_error(self, mock_get) -> None:
        mock_get.return_value = FakeResponse({}, status_code=404)

        with self.assertRaises(StockTradeNotFound):
            get_latest_stock_trade("NOPE")

    @patch.dict(
        "os.environ",
        {"APCA_API_KEY_ID": "test-key", "APCA_API_SECRET_KEY": "test-secret"},
    )
    @patch("market_data.httpx.get")
    def test_unexpected_payload_maps_to_domain_error(self, mock_get) -> None:
        mock_get.return_value = FakeResponse({"trade": {"p": "unknown"}})

        with self.assertRaises(MarketDataUnavailable):
            get_latest_stock_trade("AAPL")


if __name__ == "__main__":
    unittest.main()

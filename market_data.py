import os

import httpx


class AlpacaCredentialsError(Exception):
    """Raised when Alpaca credentials are missing or rejected."""


class StockTradeNotFound(Exception):
    """Raised when Alpaca has no latest trade for the requested ticker."""


class MarketDataUnavailable(Exception):
    """Raised when Alpaca cannot return usable market data."""


def get_latest_stock_trade(symbol: str) -> dict[str, str | float]:
    """Fetch and normalize one latest IEX trade from Alpaca."""
    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")
    if not api_key or not secret_key:
        raise AlpacaCredentialsError(
            "Alpaca credentials are not configured on the server."
        )

    try:
        response = httpx.get(
            f"https://data.alpaca.markets/v2/stocks/{symbol}/trades/latest",
            params={"feed": "iex"},
            headers={
                "APCA-API-KEY-ID": api_key,
                "APCA-API-SECRET-KEY": secret_key,
            },
            timeout=10.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as error:
        status_code = error.response.status_code
        if status_code == 404:
            raise StockTradeNotFound(
                f"No latest trade was found for ticker {symbol}."
            ) from error
        if status_code in (401, 403):
            raise AlpacaCredentialsError(
                "Alpaca rejected the credentials or market-data access."
            ) from error
        raise MarketDataUnavailable(
            "Alpaca could not provide a stock trade right now."
        ) from error
    except httpx.RequestError as error:
        raise MarketDataUnavailable(
            "Could not connect to Alpaca market data."
        ) from error

    try:
        payload = response.json()
    except ValueError as error:
        raise MarketDataUnavailable(
            "Alpaca returned an invalid stock-trade response."
        ) from error

    trade = payload.get("trade") if isinstance(payload, dict) else None
    if (
        not isinstance(trade, dict)
        or not isinstance(trade.get("p"), (int, float))
        or not isinstance(trade.get("t"), str)
    ):
        raise MarketDataUnavailable(
            "Alpaca returned an unexpected latest-trade response."
        )

    return {
        "symbol": symbol,
        "price": trade["p"],
        "timestamp": trade["t"],
        "source": "Alpaca IEX latest trade",
    }

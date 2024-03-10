import hashlib
import hmac
import json
from abc import ABC
import time

import logging
from typing import Optional

import requests

from bitkub.exception import BitkubException
from dataclasses import dataclass


@dataclass(frozen=True)
class Endpoints:
    # public endpoints
    STATUS = "/api/status"
    MARKET_SYMBOLS = "/api/market/symbols"
    MARKET_TICKER = "/api/market/ticker"
    MARKET_TRADES = "/api/market/trades"
    MARKET_BIDS = "/api/market/bids"
    MARKET_ASKS = "/api/market/asks"
    MARKET_BOOKS = "/api/market/books"
    MARKET_DEPTH = "/api/market/depth"
    TRADING_VIEW_HISTORY = "/tradingview/history"
    SERVER_TIME = "/api/v3/servertime"

    # private endpoints

    USER_LIMITS = "/api/v3/user/limits"
    USER_TRADING_CREDITS = "/api/v3/user/trading-credits"
    MARKET_WALLET = "/api/v3/market/wallet"
    MARKET_BALANCES = "/api/v3/market/balances"
    MARKET_PLACE_BID = "/api/v3/market/place-bid"
    MARKET_PLACE_ASK = "/api/v3/market/place-ask"
    MARKET_CANCEL_ORDER = "/api/v3/market/cancel-order"
    MARKET_WSTOKEN = "/api/v3/market/wstoken"
    MARKET_MY_OPEN_ORDERS = "/api/v3/market/my-open-orders"
    MARKET_MY_ORDER_HISTORY = "/api/v3/market/my-order-history"
    MARKET_ORDER_INFO = "/api/v3/market/order-info"
    CRYPTO_INTERNAL_WITHDRAW = "/api/v3/crypto/internal-withdraw"
    CRYPTO_ADDRESSES = "/api/v3/crypto/addresses"
    CRYPTO_WITHDRAW = "/api/v3/crypto/withdraw"
    CRYPTO_DEPOSIT_HISTORY = "/api/v3/crypto/deposit-history"
    CRYPTO_WITHDRAW_HISTORY = "/api/v3/crypto/withdraw-history"
    CRYPTO_GENERATE_ADDRESS = "/api/v3/crypto/generate-address"
    FIAT_ACCOUNTS = "/api/v3/fiat/accounts"
    FIAT_WITHDRAW = "/api/v3/fiat/withdraw"
    FIAT_DEPOSIT_HISTORY = "/api/v3/fiat/deposit-history"
    FIAT_WITHDRAW_HISTORY = "/api/v3/fiat/withdraw-history"


class BaseClient(ABC):
    def __init__(
        self,
        api_key: Optional[str] = "",
        api_secret: Optional[str] = "",
        base_url="https://api.bitkub.com",
        logging_level=logging.INFO,
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._api_secret = api_secret

        self.logger = logging.getLogger("bitkub")
        self.logger.setLevel(logging_level)
        self.logger.addHandler(logging.NullHandler())

    def _json_encode(self, data):
        return json.dumps(data, separators=(",", ":"), sort_keys=True)

    def _sign(self, payload_string: str):
        if not self._api_secret:
            raise BitkubException("API secret not set")
        return hmac.new(
            self._api_secret.encode("utf-8"),
            payload_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _private_headers(self, ts, sig) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-BTK-TIMESTAMP": ts,
            "X-BTK-SIGN": sig,
            "X-BTK-APIKEY": self._api_key,
        }

    def _public_headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }


class Client(BaseClient):

    def __init__(
        self,
        api_key: Optional[str] = "",
        api_secret: Optional[str] = "",
        base_url="https://api.bitkub.com",
        logging_level=logging.INFO,
    ):
        super().__init__(api_key, api_secret, base_url, logging_level)
        self.session = requests.Session()

    def _guard_errors(self, response: requests.Response):

        if response.status_code < 200 or response.status_code >= 300:
            raise BitkubException(f"{response.status_code} : {response.text} ")

    def _handle_response(self, response: requests.Response) -> dict:
        self._guard_errors(response)

        try:
            data = response.json()

        except ValueError:
            raise BitkubException("Invalid JSON response")

        return data

    def __send_request(self, method, path, body={}):

        ts = str(round(time.time() * 1000))
        str_body = json.dumps(body)
        payload = [ts, method, path, str_body]
        sig = self._sign("".join(payload))

        headers = self._private_headers(ts, sig)
        self.logger.debug("Request: %s %s %s", method, path, str_body)

        response = self.session.request(
            method, self._base_url + path, headers=headers, data=str_body
        )
        return self._handle_response(response)

    def _send_public_request(self, method, path, body={}, path_params={}):
        str_body = json.dumps(body)
        response = self.session.request(
            method,
            self._base_url + path,
            headers=super()._public_headers(),
            data=str_body,
            params=path_params,
        )
        return self._handle_response(response)

    def fetch_server_time(self):
        """
        Fetches the server time from the Bitkub API.

        Returns:
            The server time response from the API.
        """
        response = self._send_public_request("GET", Endpoints.SERVER_TIME)
        return response

    def fetch_status(self):
        """
        Fetches the status of the Bitkub API.

        Returns:
            The response from the API call.
        """
        response = self._send_public_request("GET", Endpoints.STATUS)
        return response

    def fetch_symbols(self):
        response = self._send_public_request("GET", Endpoints.MARKET_SYMBOLS)
        return response

    def fetch_tickers(self, symbol: str = ""):
        """
        Fetches tickers for a specific symbol or all symbols.

        Args:
            symbol (str, optional): The symbol for which to fetch tickers. Defaults to "" (empty string) to fetch tickers for all symbols.

        Returns:
            dict: A dictionary containing the tickers data.

        """
        response = self._send_public_request(
            "GET",
            Endpoints.MARKET_TICKER,
            path_params={"sym": symbol},
        )
        return response

    def fetch_trades(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            "GET",
            Endpoints.MARKET_TRADES,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_bids(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            "GET",
            Endpoints.MARKET_BIDS,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_asks(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            "GET",
            Endpoints.MARKET_ASKS,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_order_books(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            "GET",
            Endpoints.MARKET_BOOKS,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_depth(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            "GET",
            Endpoints.MARKET_DEPTH,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_trading_view_history(
        self,
        symbol: str = "",
        resolution: str = "",
        from_time: int = 0,
        to_time: int = 0,
    ):
        """
        Fetches trading view history for a given symbol.

        Args:
            symbol (str): The symbol to fetch trading view history for. (e.g. BTC_THB)
            resolution (str): The resolution of the trading view history data. (e.g. 1, 5, 15, 60, 240, 1D)
            from_time (int): The starting timestamp of the trading view history data. (e.g. 1633424427)
            to_time (int): The ending timestamp of the trading view history data. (e.g. 1633427427)

        Returns:
            dict: The trading view history data.

        """

        response = self._send_public_request(
            "GET",
            Endpoints.TRADING_VIEW_HISTORY,
            path_params={
                "symbol": symbol,
                "resolution": resolution,
                "from": from_time,
                "to": to_time,
            },
        )
        return response

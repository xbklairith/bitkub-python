import hashlib
import hmac
import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bitkub.exception import BitkubAPIException, BitkubException
from bitkub.models import (
    ServerTimeResponse,
    StatusResponse,
    SymbolsResponse,
    TickerResponse,
)

from . import const as c


class BaseClient(ABC):
    def __init__(
        self,
        api_key: Optional[str] = "",
        api_secret: Optional[str] = "",
        base_url: str = "https://api.bitkub.com",
        logging_level: int = logging.INFO,
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._api_secret = api_secret

        self.logger = logging.getLogger("bitkub")
        self.logger.setLevel(logging_level)
        self.logger.addHandler(logging.NullHandler())

    def _json_encode(self, data: Dict[str, Any]) -> str:
        return json.dumps(data)

    def _sign(self, payload_string: str) -> str:
        if not self._api_secret:
            raise BitkubException("API secret not set")
        return hmac.new(
            self._api_secret.encode("utf-8"),
            payload_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _private_headers(self, ts: str, sig: str) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-BTK-TIMESTAMP": ts,
            "X-BTK-SIGN": sig,
            "X-BTK-APIKEY": self._api_key or "",
        }

    def _public_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    @abstractmethod
    def _send_request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Abstract method for sending requests - must be implemented by subclasses."""
        pass


class Client(BaseClient):
    def __init__(
        self,
        api_key: Optional[str] = "",
        api_secret: Optional[str] = "",
        base_url: str = "https://api.bitkub.com",
        logging_level: int = logging.INFO,
    ) -> None:
        super().__init__(api_key, api_secret, base_url, logging_level)
        self.session = requests.Session()

    def _send_request(self, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
        """Implementation of abstract method for sending requests."""
        authenticated = kwargs.get("authenticated", True)
        body = kwargs.get("body", {})
        query_params = kwargs.get("query_params", {})
        return self._send_api_request(method, path, body, query_params, authenticated)

    def _guard_errors(self, response: requests.Response) -> None:
        """Check response status and raise exception if not successful."""
        if response.status_code < 200 or response.status_code >= 300:
            raise BitkubException(f"{response.status_code} : {response.text}")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle response, check for errors and parse JSON."""
        self._guard_errors(response)

        try:
            data = response.json()
        except ValueError as err:
            raise BitkubException("Invalid JSON response") from err

        # Check for API errors in the response
        if isinstance(data, dict) and "error" in data:
            error_code = data.get("error")
            if error_code and error_code != 0:
                error_msg = data.get("message", f"API Error {error_code}")
                raise BitkubAPIException(error_msg, error_code)

        return data  # type: ignore[no-any-return]

    def _send_api_request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        authenticated: bool = True,
    ) -> Dict[str, Any]:
        """Unified method to send API requests (both public and private)."""
        if body is None:
            body = {}
        if query_params is None:
            query_params = {}

        if authenticated:
            return self._send_private_request(method, path, body, query_params)
        else:
            return self._send_public_request(method, path, body, query_params)

    def _send_private_request(
        self, method: str, path: str, body: Dict[str, Any], query_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send authenticated request to private API endpoints."""

        ts = str(round(time.time() * 1000))
        str_body = json.dumps(body)
        if query_params:
            path = path + "?" + urlencode(query_params)
        payload = [ts, method, path, str_body]
        sig = self._sign("".join(payload))

        headers = self._private_headers(ts, sig)
        self.logger.debug("Private API Request: %s %s %s", method, path, str_body)

        response = self.session.request(
            method,
            self._base_url + path,
            headers=headers,
            data=str_body,
        )
        return self._handle_response(response)

    def _send_public_request(
        self, method: str, path: str, body: Dict[str, Any], query_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send unauthenticated request to public API endpoints."""
        str_body = json.dumps(body)
        self.logger.debug("Public API Request: %s %s %s", method, path, str_body)

        response = self.session.request(
            method,
            self._base_url + path,
            headers=self._public_headers(),
            data=str_body,
            params=query_params,
        )
        return self._handle_response(response)

    def __send_request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Legacy private method - kept for backward compatibility."""
        return self._send_private_request(method, path, body or {}, query_params or {})

    def fetch_server_time(self) -> Dict[str, Any]:
        """
        Fetches the server time from the Bitkub API.

        Returns:
            The server time response from the API.
        """
        response = self._send_public_request(c.GET, c.Endpoints.SERVER_TIME, {}, {})
        return response

    def fetch_server_time_typed(self) -> ServerTimeResponse:
        """Fetch server time with typed response."""
        response = self.fetch_server_time()
        return ServerTimeResponse.from_dict(response)

    def fetch_status(self) -> Dict[str, Any]:
        """
        Fetches the status of the Bitkub API.

        Returns:
            The response from the API call.
        """
        response = self._send_public_request(c.GET, c.Endpoints.STATUS, {}, {})
        return response

    def fetch_status_typed(self) -> StatusResponse:
        """Fetch API status with typed response."""
        response = self.fetch_status()
        return StatusResponse.from_dict(response)

    def fetch_symbols(self) -> Dict[str, Any]:
        """Fetch available trading symbols."""
        response = self._send_public_request(c.GET, c.Endpoints.MARKET_SYMBOLS, {}, {})
        return response

    def fetch_symbols_typed(self) -> SymbolsResponse:
        """Fetch available trading symbols with typed response."""
        response = self.fetch_symbols()
        return SymbolsResponse.from_dict(response)

    def fetch_tickers(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches tickers for a specific symbol or all symbols.

        Args:
            symbol: The symbol for which to fetch tickers. None to fetch all symbols.

        Returns:
            dict: A dictionary containing the tickers data.
        """
        params = {"sym": symbol} if symbol else {}
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_TICKER,
            {},
            params,
        )
        return response

    def fetch_tickers_typed(self, symbol: Optional[str] = None) -> TickerResponse:
        """Fetch tickers with typed response."""
        response = self.fetch_tickers(symbol)
        return TickerResponse.from_dict(response)

    def fetch_trades(self, symbol: str = "", limit: int = 10) -> Dict[str, Any]:
        """Fetch recent trades for a symbol."""
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_TRADES,
            {},
            {"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_bids(self, symbol: str = "", limit: int = 10) -> Dict[str, Any]:
        """Fetch bid orders for a symbol."""
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_BIDS,
            {},
            {"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_asks(self, symbol: str = "", limit: int = 10) -> Dict[str, Any]:
        """Fetch ask orders for a symbol."""
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_ASKS,
            {},
            {"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_order_books(self, symbol: str = "", limit: int = 10) -> Dict[str, Any]:
        """Fetch order book for a symbol."""
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_BOOKS,
            {},
            {"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_depth(self, symbol: str = "", limit: int = 10) -> Dict[str, Any]:
        """Fetch market depth for a symbol."""
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_DEPTH,
            {},
            {"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_trading_view_history(
        self,
        symbol: str = "",
        resolution: str = "",
        from_time: int = 0,
        to_time: int = 0,
    ) -> Dict[str, Any]:
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
            c.GET,
            c.Endpoints.TRADING_VIEW_HISTORY,
            {},
            {
                "symbol": symbol,
                "resolution": resolution,
                "from": from_time,
                "to": to_time,
            },
        )
        return response

    def fetch_user_limits(self) -> Dict[str, Any]:
        """
        Fetches the user's trading limits.

        Returns:
            dict: A dictionary containing the response from the API call. The dictionary has two keys:
                - "error" (int): The error code. 0 indicates success.
                - "result" (dict): The trading limits.
        """
        response = self.__send_request(c.POST, c.Endpoints.USER_LIMITS)
        return response

    def fetch_user_trade_credit(self) -> Dict[str, Any]:
        """
        Fetches the user's trade credit.

        Returns:
            dict: A dictionary containing the response from the API call. The dictionary has two keys:
                - "error" (int): The error code. 0 indicates success.
                - "result" (int): The trade credit amount.

        Example:
            {
                "error": 0,
                "result": 1000
            }
        """
        response = self.__send_request(c.POST, c.Endpoints.USER_TRADING_CREDITS)
        return response

    def fetch_wallet(self) -> Dict[str, Any]:
        """
        Fetches the user's market wallet.

        Returns:
            dict: A dictionary containing the response from the API call. The dictionary has two keys:
                - "error" (int): The error code. 0 indicates success.
                - "result" (dict): The market wallet data.

        Example:
            {
                "error": 0,
                "result": {
                    "THB": 1000,
                    "BTC": 0.1
                }
            }
        """
        response = self.__send_request(c.POST, c.Endpoints.MARKET_WALLET)
        return response

    def fetch_balances(self) -> Dict[str, Any]:
        """
        Fetches the user's market balances.

        Returns:
            dict: A dictionary containing the response from the API call. The dictionary has two keys:
                - "error" (int): The error code. 0 indicates success.
                - "result" (dict): The market balances data.

        Example:
            {
                "error": 0,
                "result": {
                    "THB":  {
                    "available": 188379.27,
                    "reserved": 0
                    },
                    "BTC": {
                    "available": 8.90397323,
                    "reserved": 0
                    },
                    "ETH": {
                    "available": 10.1,
                    "reserved": 0
                    }
                }
            }
        """
        response = self.__send_request(c.POST, c.Endpoints.MARKET_BALANCES)
        return response

    def create_order_buy(
        self,
        symbol: str,
        amount: float,
        rate: float,
        type: str = "limit",
        client_id: str = "",
    ) -> Dict[str, Any]:
        """
        Creates a buy order in the Bitkub marketplace.

        Args:
            symbol (str): The symbol of the cryptocurrency to buy.
            amount (float): The amount of THB (Thai Baht) to spend on the buy order.
            rate (float): The rate at which to buy the cryptocurrency.
            type (str, optional): The type of order. Defaults to "limit".
            client_id (str, optional): The client ID for the order. Defaults to "".

        Returns:
            dict: A dictionary containing the response from the API call. The dictionary has two keys:
                - "error" (int): The error code. 0 indicates success.
                - "result" (dict): The order data.
        """
        body = {
            "sym": symbol,
            "amt": amount,  # amount of THB
            "rat": rate,
            "typ": type,
            "client_id": client_id,
        }
        response = self.__send_request(c.POST, c.Endpoints.MARKET_PLACE_BID, body=body)
        return response

    def create_order_sell(
        self,
        symbol: str,
        amount: float,
        rate: float,
        type: str = "limit",
        client_id: str = "",
    ) -> Dict[str, Any]:
        """
        Creates a sell order for the specified symbol.

        Args:
            symbol (str): The symbol of the coin to sell.
            amount (float): The amount of the coin to sell.
            rate (float): The rate at which to sell the coin.
            type (str, optional): The type of order. Defaults to "limit".
            client_id (str, optional): The client ID for the order. Defaults to "".

        Returns:
            dict: The response from the API.

        """
        body = {
            "sym": symbol,
            "amt": amount,  # amount of coin
            "rat": rate,
            "typ": type,
            "client_id": client_id,
        }
        response = self.__send_request(c.POST, c.Endpoints.MARKET_PLACE_ASK, body=body)
        return response

    def cancel_order(
        self, symbol: str = "", id: str = "", side: str = "", hash: str = ""
    ) -> Dict[str, Any]:
        """
        Cancels an order on the Bitkub exchange.

        Args:
            symbol (str): The trading pair symbol (e.g., "BTC_THB").
            id (str): The order ID to cancel.
            side (str): The order side ("buy" or "sell").
            hash (str): The order hash.

        Returns:
            dict: The response from the API.

        """

        body = {
            "sym": symbol,
            "id": id,
            "sd": side,
            "hash": hash,
        }
        response = self.__send_request(
            c.POST, c.Endpoints.MARKET_CANCEL_ORDER, body=body
        )
        return response

    def create_websocket_token(self) -> Dict[str, Any]:
        """Create a websocket token for real-time data."""
        response = self.__send_request(c.POST, c.Endpoints.MARKET_WSTOKEN)
        return response

    def fetch_open_orders(self, symbol: str) -> Dict[str, Any]:
        """Fetch open orders for a symbol."""
        response = self.__send_request(
            c.GET, c.Endpoints.MARKET_MY_OPEN_ORDERS, query_params={"sym": symbol}
        )
        return response

    def fetch_order_history(
        self,
        symbol: str,
        page: int = 1,
        limit: int = 10,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Fetch order history for a symbol with optional pagination and time filters."""
        params: Dict[str, Any] = {"sym": symbol}
        if page:
            params["p"] = page
        if limit:
            params["lmt"] = limit
        if start_time:
            params["start"] = start_time
        if end_time:
            params["end"] = end_time

        response = self.__send_request(
            c.GET, c.Endpoints.MARKET_MY_ORDER_HISTORY, query_params=params
        )
        return response

    def fetch_order_info(
        self, symbol: str = "", id: str = "", side: str = "", hash: str = ""
    ) -> Dict[str, Any]:
        """Fetch information about a specific order."""
        params: Dict[str, Any] = {}
        if symbol:
            params["sym"] = symbol
        if id:
            params["id"] = id
        if side:
            params["sd"] = side
        if hash:
            params["hash"] = hash

        response = self.__send_request(
            c.GET, c.Endpoints.MARKET_ORDER_INFO, query_params=params
        )
        return response

    def withdraw(
        self,
        currency: str,
        amount: float,
        address: str,
        network: str,
        memo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Withdraws a specified amount of cryptocurrency to the given address.

        Args:
            currency (str): The currency symbol of the cryptocurrency to withdraw.
            amount (float): The amount of cryptocurrency to withdraw.
            address (str): The destination address
            network (str): The network or blockchain on which the cryptocurrency operates.
            memo (str): The memo or tag associated with the withdrawal (if applicable).

        Returns:
            dict: The response from the API containing information about the withdrawal.

        """

        body = {
            "cur": currency,
            "amt": amount,
            "adr": address,
            "mem": memo,
            "net": network,
        }

        response = self.__send_request(c.POST, c.Endpoints.CRYPTO_WITHDRAW, body=body)
        return response

    def fetch_addresses(self) -> Dict[str, Any]:
        """
        Fetches the deposit addresses for all cryptocurrencies.

        Example Response:
        .. code-block:: json
        {
            "error": 0,
            "result": [
                {
                    "currency": "BTC",
                    "address": "3BtxdKw6XSbneNvmJTLVHS9XfNYM7VAe8k",
                    "tag": 0,
                    "time": 1570893867
                }
            ],
            "pagination": {
                "page": 1,
                "last": 1
            }
        }
        """
        response = self.__send_request(c.POST, c.Endpoints.CRYPTO_ADDRESSES)
        return response

    def fetch_deposits(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Fetches the deposit history for the user.

        Example Response:
        .. code-block:: json
        {
            "error": 0,
            "result": [
                {
                    "hash": "XRPWD0000100276",
                    "currency": "XRP",
                    "amount": 5.75111474,
                    "from_address": "sender address",
                    "to_address": "recipient address",
                    "confirmations": 1,
                    "status": "complete",
                    "time": 1570893867
                }
            ],
            "pagination": {
                "page": 1,
                "last": 1
            }
        }
        """

        params = {"p": page, "lmt": limit}
        response = self.__send_request(
            c.POST, c.Endpoints.CRYPTO_DEPOSIT_HISTORY, query_params=params
        )
        return response

    def fetch_withdrawals(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Fetches the withdrawal history for the user.

        Example Response:
        .. code-block:: json
        {
            "error": 0,
            "result": [
                {
                    "txn_id": "XRPWD0000100276",
                    "hash": "send_internal",
                    "currency": "XRP",
                    "amount": "5.75111474",
                    "fee": 0.01,
                    "address": "rpXTzCuXtjiPDFysxq8uNmtZBe9Xo97JbW",
                    "status": "complete",
                    "time": 1570893493
                }
            ],
            "pagination": {
                "page": 1,
                "last": 1
            }
        }
        """

        params = {"p": page, "lmt": limit}
        response = self.__send_request(
            c.POST, c.Endpoints.CRYPTO_WITHDRAW_HISTORY, query_params=params
        )
        return response

    def fetch_fiat_accounts(self) -> Dict[str, Any]:
        """
        Fetches the fiat accounts associated with the client.

        Example Response:
        .. code-block:: json
        {
            "error": 0,
            "result": [
                {
                    "id": "7262109099",
                    "bank": "Kasikorn Bank",
                    "name": "Somsak",
                    "time": 1570893867
                }
            ],
            "pagination": {
                "page": 1,
                "last": 1
            }
        }
        """
        response = self.__send_request(c.POST, c.Endpoints.FIAT_ACCOUNTS)
        return response

    def withdraw_fiat(self, bank_id: str, amount: float) -> Dict[str, Any]:
        """
        Withdraws fiat currency from the Bitkub exchange.

        Args:
            bank_id (str): The ID of the bank account to withdraw to.
            amount (float): The amount of fiat currency to withdraw.

        Returns:
            dict: The response from the API.

        """
        body = {"amt": amount, "id": bank_id}
        response = self.__send_request(c.POST, c.Endpoints.FIAT_WITHDRAW, body=body)
        return response

    def fetch_fiat_deposits(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Fetches the fiat deposit history for the user.

        Example Response:
        .. code-block:: json
        {
            "error": 0,
            "result": [
                {
                    "txn_id": "THBDP0000012345",
                    "currency": "THB",
                    "amount": 5000.55,
                    "status": "complete",
                    "time": 1570893867
                }
            ],
            "pagination": {
                "page": 1,
                "last": 1
            }
        }
        """
        params = {"p": page, "lmt": limit}
        response = self.__send_request(
            c.POST, c.Endpoints.FIAT_DEPOSIT_HISTORY, query_params=params
        )
        return response

    def fetch_fiat_withdrawals(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Fetches the fiat withdrawal history for the user.

        Example Response:
        .. code-block:: json
        {
            "error":0,
            "result": [
                {
                    "txn_id": "THBWD0000012345",
                    "currency": "THB",
                    "amount": "21",
                    "fee": 20,
                    "status": "complete",
                    "time": 1570893493
                }
            ],
            "pagination": {
                "page": 1,
                "last": 1
            }
        }
        """
        params = {"p": page, "lmt": limit}
        response = self.__send_request(
            c.POST, c.Endpoints.FIAT_WITHDRAW_HISTORY, query_params=params
        )
        return response

    # V4 Crypto API methods
    def fetch_crypto_addresses_v4(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        symbol: Optional[str] = None,
        network: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch crypto addresses using v4 API."""
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if symbol:
            params["symbol"] = symbol
        if network:
            params["network"] = network
        if memo:
            params["memo"] = memo

        response = self._send_api_request(
            c.GET, c.Endpoints.CRYPTO_V4_ADDRESSES, query_params=params
        )
        return response

    def generate_crypto_address_v4(self, symbol: str, network: str) -> Dict[str, Any]:
        """Generate new crypto address using v4 API."""
        body = {"symbol": symbol, "network": network}
        response = self._send_api_request(
            c.POST, c.Endpoints.CRYPTO_V4_ADDRESSES, body=body
        )
        return response

    def fetch_crypto_deposits_v4(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        created_start: Optional[int] = None,
        created_end: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Fetch crypto deposit history using v4 API."""
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        if created_start is not None:
            params["created_start"] = created_start
        if created_end is not None:
            params["created_end"] = created_end

        response = self._send_api_request(
            c.GET, c.Endpoints.CRYPTO_V4_DEPOSITS, query_params=params
        )
        return response

    def fetch_crypto_withdraws_v4(
        self,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        created_start: Optional[int] = None,
        created_end: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Fetch crypto withdrawal history using v4 API."""
        params: Dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit
        if symbol:
            params["symbol"] = symbol
        if status:
            params["status"] = status
        if created_start is not None:
            params["created_start"] = created_start
        if created_end is not None:
            params["created_end"] = created_end

        response = self._send_api_request(
            c.GET, c.Endpoints.CRYPTO_V4_WITHDRAWS, query_params=params
        )
        return response

    def fetch_crypto_coins_v4(self) -> Dict[str, Any]:
        """Fetch available cryptocurrencies using v4 API."""
        response = self._send_api_request(c.GET, c.Endpoints.CRYPTO_V4_COINS)
        return response

    def fetch_crypto_compensations_v4(self) -> Dict[str, Any]:
        """Fetch compensation information using v4 API."""
        response = self._send_api_request(c.GET, c.Endpoints.CRYPTO_V4_COMPENSATIONS)
        return response

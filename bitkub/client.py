import hashlib
import hmac
import json
from abc import ABC
import time

import logging
from typing import Optional

import requests

from bitkub.exception import BitkubException
from . import const as c


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
        return json.dumps(data)

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

        # functools pratial

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
        response = self._send_public_request(c.GET, c.Endpoints.SERVER_TIME)
        return response

    def fetch_status(self):
        """
        Fetches the status of the Bitkub API.

        Returns:
            The response from the API call.
        """
        response = self._send_public_request(c.GET, c.Endpoints.STATUS)
        return response

    def fetch_symbols(self):
        response = self._send_public_request(c.GET, c.Endpoints.MARKET_SYMBOLS)
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
            c.GET,
            c.Endpoints.MARKET_TICKER,
            path_params={"sym": symbol},
        )
        return response

    def fetch_trades(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_TRADES,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_bids(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_BIDS,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_asks(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_ASKS,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_order_books(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_BOOKS,
            path_params={"sym": symbol, "lmt": limit},
        )
        return response

    def fetch_depth(self, symbol: str = "", limit: int = 10):
        response = self._send_public_request(
            c.GET,
            c.Endpoints.MARKET_DEPTH,
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
            c.GET,
            c.Endpoints.TRADING_VIEW_HISTORY,
            path_params={
                "symbol": symbol,
                "resolution": resolution,
                "from": from_time,
                "to": to_time,
            },
        )
        return response

    def fetch_user_limits(self):
        """
        Fetches the user's trading limits.

        Returns:
            dict: A dictionary containing the response from the API call. The dictionary has two keys:
                - "error" (int): The error code. 0 indicates success.
                - "result" (dict): The trading limits.
        """
        response = self.__send_request(c.POST, c.Endpoints.USER_LIMITS)
        return response

    def fetch_user_trade_credit(self):
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

    def fetch_wallet(self):
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

    def fetch_balances(self):
        """
        fetches the user's market balances.


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
    ):
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
    ):
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
    ):
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

    def create_websocket_token(self):
        response = self.__send_request(c.POST, c.Endpoints.MARKET_WSTOKEN)
        return response

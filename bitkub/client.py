import hashlib
import hmac
import json
from abc import ABC
from typing import Any, Dict

import requests

from bitkub.exception import BitkubException


class BaseClient(ABC):
    def __init__(
        self, api_key=None, api_secret=None, base_url="https://api.bitkub.com"
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._api_secret = api_secret

    def json_encode(self, data):
        return json.dumps(data, separators=(",", ":"), sort_keys=True)

    def sign(self, data):
        if self._api_secret is None:
            raise BitkubException("API secret not set")
        j = self.json_encode(data)
        h = hmac.new(
            str.encode(self.api_secret), msg=j.encode(), digestmod=hashlib.sha256
        )
        return h.hexdigest()


class Client(BaseClient):
    def _make_request(self, method, endpoint, **kwargs):
        response = requests.request(method, f"{self.base_url}/{endpoint}", **kwargs)
        return response.json()

    def _get(self, endpoint, **kwargs) -> Dict[str, Any]:
        return self._make_request("GET", endpoint, **kwargs)

    def _post(self, endpoint, data=None, json=None, **kwargs) -> Dict[str, Any]:
        return self._make_request("POST", endpoint, data=data, json=json, **kwargs)

    def get_server_info(self):
        return self._get("api/server")

    def post_order(self, data):
        return self._post("api/order", json=data)

    def get_orders(self):
        return self._get("api/order")

import hashlib
import hmac
import json
from abc import ABC
import time

import logging

import requests

from bitkub.exception import BitkubException


class BaseClient(ABC):
    def __init__(
        self,
        api_key="",
        api_secret="",
        base_url="https://api.bitkub.com",
        logging_level=logging.INFO,
    ):
        self._base_url = base_url
        self._api_key = api_key
        self._api_secret = api_secret

        self.logger = logging.getLogger("bitkub")
        self.logger.setLevel(logging_level)
        self.logger.addHandler(logging.NullHandler())

    def json_encode(self, data):
        return json.dumps(data, separators=(",", ":"), sort_keys=True)

    def sign(self, payload_string: str):
        return hmac.new(
            self._api_secret.encode("utf-8"),
            payload_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def headers(self, ts, sig):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-BTK-TIMESTAMP": ts,
            "X-BTK-SIGN": sig,
            "X-BTK-APIKEY": self._api_key,
        }


class Client(BaseClient):
    def handle_response(self, response):
        try:
            data = response.json()
        except ValueError:
            data = response.text
        if response.status_code != 200:
            raise BitkubException(data)
        return data

    def send_request(self, method, path, body={}):

        ts = str(round(time.time() * 1000))
        str_body = json.dumps(body)
        payload = [ts, method, path, str_body]
        sig = self.sign("".join(payload))

        headers = self.headers(ts, sig)
        self.logger.debug("Request: %s %s %s", method, path, str_body)

        response = requests.request(
            method, self._base_url + path, headers=headers, data=str_body
        )
        return self.handle_response(response)

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

    def private_headers(self, ts, sig) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-BTK-TIMESTAMP": ts,
            "X-BTK-SIGN": sig,
            "X-BTK-APIKEY": self._api_key,
        }

    def public_headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }


class Client(BaseClient):

    def __init__(
        self,
        api_key="",
        api_secret="",
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

    def send_request(self, method, path, body={}):

        ts = str(round(time.time() * 1000))
        str_body = json.dumps(body)
        payload = [ts, method, path, str_body]
        sig = self.sign("".join(payload))

        headers = self.private_headers(ts, sig)
        self.logger.debug("Request: %s %s %s", method, path, str_body)

        response = self.session.request(
            method, self._base_url + path, headers=headers, data=str_body
        )
        return self._handle_response(response)

    def send_public_request(self, method, path, body={}):
        str_body = json.dumps(body)
        response = requests.request(
            method, self._base_url + path, headers=self.public_headers(), data=str_body
        )
        return self._handle_response(response)

    def status(self):
        """
        Get status of the API server

        :return: dict
        """

        response = self.send_public_request("GET", "/api/status")
        return response

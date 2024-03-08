import requests_mock
from bitkub import Client

import pytest

from bitkub.exception import BitkubException


def test_client():
    from bitkub import Client

    client = Client(api_key="api-key", api_secret="api-secret")
    assert client._api_key == "api-key"
    assert client._api_secret == "api-secret"


def test_get_status(mock_client: Client, with_request_status_ok: None):
    response = mock_client.status()
    assert response[0].get("status", {}) == "ok"


def test_get_status_error(mock_client: Client, with_request_status_error: None):
    # expect an exception to be raised on 400 status code
    with pytest.raises(BitkubException):
        mock_client.status()


def test_get_status_error_invalid_json(
    mock_client: Client, with_request_status_invalid_json: None
):
    # expect an exception to be raised on 400 status code
    with pytest.raises(BitkubException):
        mock_client.status()


def test_get_tickers(mock_client: Client, with_request_tickers):

    response = mock_client.tickers()
    assert response.get("THB_BTC", {}).get("baseVolume") == 215.23564897
    assert response.get("THB_ETH", {}).get("percentChange") == 1.89


def test_get_tickers_by_symbol(
    mock_client: Client,
    mock_requests: requests_mock.Mocker,
):
    matcher = mock_requests.get("/api/market/ticker?sym=THB_BTC", json={"THB_BTC": {}})
    mock_client.tickers("THB_BTC")

    assert matcher.called_once

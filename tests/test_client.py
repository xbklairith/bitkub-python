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
    response = mock_client.fetch_status()
    assert response[0].get("status", {}) == "ok"


def test_get_status_error(mock_client: Client, with_request_status_error: None):
    # expect an exception to be raised on 400 status code
    with pytest.raises(BitkubException):
        mock_client.fetch_status()


def test_get_status_error_invalid_json(
    mock_client: Client, with_request_status_invalid_json: None
):
    # expect an exception to be raised on 400 status code
    with pytest.raises(BitkubException):
        mock_client.fetch_status()


def test_get_tickers(mock_client: Client, with_request_tickers):

    response = mock_client.fetch_tickers()
    assert response.get("THB_BTC", {}).get("baseVolume") == 215.23564897
    assert response.get("THB_ETH", {}).get("percentChange") == 1.89


def test_get_tickers_by_symbol(
    mock_client: Client,
    mock_requests: requests_mock.Mocker,
):
    matcher = mock_requests.get("/api/market/ticker?sym=THB_BTC", json={"THB_BTC": {}})
    mock_client.fetch_tickers("THB_BTC")

    assert matcher.called


def test_fetch_user_trade_credit(
    mock_client: Client, with_request_user_trade_credit: None
):
    response = mock_client.fetch_user_trade_credit()
    assert response.get("error") == 0
    assert response.get("result") == 1000


def test_fetch_user_limits(mock_client: Client, with_request_user_limits: None):
    response = mock_client.fetch_user_limits()
    assert response.get("error") == 0
    assert "limits" in response.get("result", {}).keys()
    assert "usage" in response.get("result", {}).keys()
    assert response["result"]["limits"]["fiat"]["withdraw"] == 5000000


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("fetch_wallet", "/api/v3/market/wallet"),
        ("fetch_balances", "/api/v3/market/balances"),
    ],
)
def test_fetch_market_called_endpoint(
    method,
    endpoint,
    mock_client: Client,
    mock_requests: requests_mock.Mocker,
):
    matcher = mock_requests.post(endpoint, json={"symbols": []})
    getattr(mock_client, method)()
    assert matcher.called


def test_create_order_buy(
    mock_client: Client,
    with_create_order_buy: None,
):
    response = mock_client.create_order_buy(symbol="THB_BTC", amount=10, rate=10000000)
    assert response.get("error") == 0
    assert response.get("result", {}).get("id") == "54583082"
    assert response.get("result", {}).get("hash") == "fwQ6dnQWTQMygWR3HsiAatTK1B6"


def test_create_order_sell(
    mock_client: Client,
    with_create_order_sell: None,
):
    response = mock_client.create_order_sell(symbol="THB_BTC", amount=10, rate=10000000)
    assert response.get("error") == 0
    assert response.get("result", {}).get("id") == "54583082"
    assert response.get("result", {}).get("hash") == "fwQ6dnQWTQMygWR3HsiAatTK1B6"


def test_create_order_buy_correct_request(
    mock_client: Client,
    mock_requests: requests_mock.Mocker,
):
    matcher = mock_requests.post("/api/v3/market/place-bid", json={"error": 0})
    response = mock_client.create_order_buy(symbol="THB_BTC", amount=10, rate=10000000)
    assert response.get("error") == 0
    assert matcher.called
    assert matcher.last_request is not None
    assert matcher.last_request.json() == {
        "sym": "THB_BTC",
        "amt": 10,
        "rat": 10000000,
        "typ": "limit",
        "client_id": "",
    }


def test_create_order_sell_correct_request(
    mock_client: Client,
    mock_requests: requests_mock.Mocker,
):
    matcher = mock_requests.post("/api/v3/market/place-ask", json={"error": 0})

    response = mock_client.create_order_sell(symbol="THB_BTC", amount=10, rate=10000000)
    assert response.get("error") == 0
    assert matcher.called
    assert matcher.last_request is not None
    assert matcher.last_request.json() == {
        "sym": "THB_BTC",
        "amt": 10,
        "rat": 10000000,
        "typ": "limit",
        "client_id": "",
    }


def test_cancel_order_corect_request(
    mock_client: Client,
    mock_requests: requests_mock.Mocker,
):
    matcher = mock_requests.post("/api/v3/market/cancel-order", json={"error": 0})
    response = mock_client.cancel_order(hash="fwQ6dn")
    assert response.get("error") == 0

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
    assert matcher.called


def test_create_websocket_token(
    mock_client: Client,
    mock_requests: requests_mock.Mocker,
):
    mock_requests.post(
        "/api/v3/market/wstoken", json={"error": 0, "result": "token-xxs0dsf0"}
    )
    resp = mock_client.create_websocket_token()
    assert resp.get("error") == 0
    assert "result" in resp.keys()


def test_fetch_open_orders(mock_client: Client, with_fetch_open_order_success):
    response = mock_client.fetch_open_orders(symbol="THB_BTC")
    assert response.get("error") == 0
    assert len(response.get("result", [])) > 0


@pytest.mark.parametrize(
    "params,expected_uri",
    [
        ({"symbol": "THB_BTC", "page": 1, "limit": 10}, "sym=THB_BTC&page=1&limit=10"),
        ({"symbol": "THB_BTC", "page": 1}, "sym=THB_BTC&page=1"),
        ({"symbol": "THB_BTC", "limit": 10}, "sym=THB_BTC&limit=10"),
        ({"symbol": "THB_BTC"}, "sym=THB_BTC"),
        ({"symbol": "THB_BTC", "start_time": 11123}, "sym=THB_BTC&start_time=11123"),
        ({"symbol": "THB_BTC", "end_time": 11123}, "sym=THB_BTC&end_time=11123"),
        (
            {"symbol": "THB_BTC", "start_time": 111111111, "end_time": 22222222},
            "sym=THB_BTC&start_time=111111111&end_time=22222222",
        ),
    ],
)
def test_fetch_order_history_assert_query_params(
    mock_client: Client, mock_requests: requests_mock.Mocker, params, expected_uri
):
    matcher = mock_requests.get(
        "/api/v3/market/my-order-history",
        json={
            "error": 0,
            "pagination": {"last": 1, "page": 1},
            "result": [],
        },
    )
    mock_client.fetch_order_history(**params)
    matcher.last_request.query == expected_uri  # type: ignore


def test_fetch_order_history(mock_client: Client, with_fetch_order_history_success):
    response = mock_client.fetch_order_history(symbol="THB_BTC")
    assert response.get("error") == 0
    assert response.get("pagination", {}).get("last") == 1
    assert len(response.get("result", [])) > 0
    assert response.get("result", [])[0].get("order_id") == "23423423"


@pytest.mark.parametrize(
    "params,expected_uri",
    [
        ({"hash": "23423423"}, "hash=23423423"),
        (
            {"symbol": "THB_BTC", "side": "buy", "id": "123423"},
            "sym=THB_BTC&side=buy&id=123423",
        ),
    ],
)
def test_fetch_order_info_assert_query_params(
    mock_client: Client, mock_requests: requests_mock.Mocker, params, expected_uri
):
    matcher = mock_requests.get(
        "/api/v3/market/order-info",
        json={
            "error": 0,
            "result": [],
        },
    )
    mock_client.fetch_order_info(hash="23423423")
    assert matcher.called
    assert matcher.last_request.query == "hash=23423423"  # type: ignore


def test_withdraw(mock_client: Client, with_withdraw_success):
    response = mock_client.withdraw(
        currency="BTC",
        amount=10,
        address="1Ax20320423l23423",
        network="BTC",
    )
    assert response.get("error") == 0
    assert response.get("result", {}).get("txn") == "KKKWD0007382474"


def test_withdraw_memo(mock_client: Client, with_withdraw_success):
    response = mock_client.withdraw(
        currency="XRP",
        amount=10,
        address="1Ax20320423l23423",
        network="XRP",
        memo="123123",
    )
    assert response.get("error") == 0
    assert response.get("result", {}).get("txn") == "KKKWD0007382474"


def test_fetch_addresses(
    mock_client: Client,
    with_fetch_addresses_success,
):
    response = mock_client.fetch_addresses()
    assert response.get("error") == 0
    assert len(response.get("result", [])) > 0


def test_fetch_withdrawals(
    mock_client: Client,
    with_fetch_withdrawals_success,
):
    response = mock_client.fetch_withdrawals()
    assert response.get("error") == 0
    assert len(response.get("result", [])) > 0


def test_fetch_deposits(
    mock_client: Client,
    with_fetch_deposits_success,
):
    response = mock_client.fetch_deposits()
    assert response.get("error") == 0
    assert len(response.get("result", [])) > 0


def test_fetch_fiat_accounts(
    mock_client: Client,
    with_fetch_fiat_accounts_success,
):

    response = mock_client.fetch_fiat_accounts()
    assert response.get("error") == 0
    assert len(response.get("result", [])) > 0
    assert response.get("result", [])[0].get("id") == "7262109099"


def test_withdraw_fiat(
    mock_client: Client,
    with_withdraw_fiat_success,
):
    response = mock_client.withdraw_fiat("7262109099", 100)
    assert response.get("error") == 0
    assert response.get("result", {}).get("acc") == "7262109099"

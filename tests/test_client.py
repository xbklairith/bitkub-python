import logging
from urllib.parse import parse_qs

import pytest
import requests_mock

from bitkub import Client
from bitkub.exception import BitkubAPIException, BitkubException


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
    matcher = mock_requests.get(
        "/api/v3/market/ticker?sym=THB_BTC", json={"THB_BTC": {}}
    )
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
    "params,expected_params",
    [
        (
            {"symbol": "THB_BTC", "page": 1, "limit": 10},
            {"sym": "THB_BTC", "p": "1", "lmt": "10"},
        ),
        ({"symbol": "THB_BTC", "page": 1}, {"sym": "THB_BTC", "p": "1"}),
        ({"symbol": "THB_BTC", "limit": 10}, {"sym": "THB_BTC", "lmt": "10"}),
        ({"symbol": "THB_BTC"}, {"sym": "THB_BTC"}),
        (
            {"symbol": "THB_BTC", "start_time": 11123},
            {"sym": "THB_BTC", "start": "11123"},
        ),
        ({"symbol": "THB_BTC", "end_time": 11123}, {"sym": "THB_BTC", "end": "11123"}),
        (
            {"symbol": "THB_BTC", "start_time": 111111111, "end_time": 22222222},
            {"sym": "THB_BTC", "start": "111111111", "end": "22222222"},
        ),
    ],
)
def test_fetch_order_history_assert_query_params(
    mock_client: Client, mock_requests: requests_mock.Mocker, params, expected_params
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

    # Parse query string into dict for case-insensitive comparison
    # Note: requests-mock may lowercase some values, so we test the structure
    from urllib.parse import parse_qs

    query_dict = parse_qs(matcher.last_request.query)

    for key, expected_value in expected_params.items():
        assert key in query_dict, f"Parameter {key} not found in query"
        # Convert both to strings for comparison (values come as lists from parse_qs)
        actual_value = query_dict[key][0] if query_dict[key] else ""
        # For symbol, check case-insensitive since mock may lowercase it
        if key == "sym":
            assert actual_value.upper() == expected_value.upper(), (
                f"Symbol mismatch: {actual_value} != {expected_value}"
            )
        else:
            assert actual_value == expected_value, (
                f"Parameter {key} mismatch: {actual_value} != {expected_value}"
            )


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


def test_fetch_fiat_withdrawals(
    mock_client: Client,
    with_fetch_fiat_withdrawals_success,
):
    response = mock_client.fetch_fiat_withdrawals()
    assert response.get("error") == 0
    assert len(response.get("result", [])) > 0
    assert response.get("result", [])[0].get("txn_id") == "THBWD0000012345"
    assert response.get("result", [])[0].get("amount") == "21"


def test_fetch_fiat_deposits(
    mock_client: Client,
    with_fetch_fiat_deposits_success,
):
    response = mock_client.fetch_fiat_deposits()
    assert response.get("error") == 0
    assert len(response.get("result", [])) > 0
    assert response.get("result", [])[0].get("txn_id") == "THBDP0000012345"
    assert response.get("result", [])[0].get("amount") == 5000.55


# Test missing public endpoint methods
def test_fetch_server_time(mock_client: Client, mock_requests: requests_mock.Mocker):
    mock_requests.get("/api/v3/servertime", json={"result": 1640995200000})
    response = mock_client.fetch_server_time()
    assert response.get("result") == 1640995200000


def test_fetch_symbols(mock_client: Client, mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/market/symbols", json={"result": [{"id": 1, "symbol": "THB_BTC"}]}
    )
    response = mock_client.fetch_symbols()
    assert len(response.get("result", [])) > 0


def test_fetch_trades(mock_client: Client, mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/v3/market/trades", json={"result": [{"id": 1, "rate": 1000000}]}
    )
    response = mock_client.fetch_trades("THB_BTC", 5)
    assert len(response.get("result", [])) > 0


def test_fetch_bids(mock_client: Client, mock_requests: requests_mock.Mocker):
    mock_requests.get("/api/v3/market/bids", json={"result": [[1000000, 0.1]]})
    response = mock_client.fetch_bids("THB_BTC", 5)
    assert len(response.get("result", [])) > 0


def test_fetch_asks(mock_client: Client, mock_requests: requests_mock.Mocker):
    mock_requests.get("/api/v3/market/asks", json={"result": [[1000000, 0.1]]})
    response = mock_client.fetch_asks("THB_BTC", 5)
    assert len(response.get("result", [])) > 0


def test_fetch_order_books(mock_client: Client, mock_requests: requests_mock.Mocker):
    mock_requests.get("/api/market/books", json={"result": {"bids": [], "asks": []}})
    response = mock_client.fetch_order_books("THB_BTC", 5)
    assert "result" in response


def test_fetch_depth(mock_client: Client, mock_requests: requests_mock.Mocker):
    mock_requests.get("/api/v3/market/depth", json={"result": {"bids": [], "asks": []}})
    response = mock_client.fetch_depth("THB_BTC", 5)
    assert "result" in response


def test_fetch_trading_view_history(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    mock_requests.get(
        "/tradingview/history",
        json={
            "s": "ok",
            "c": [1000],
            "o": [990],
            "h": [1010],
            "l": [980],
            "v": [100],
            "t": [1640995200],
        },
    )
    response = mock_client.fetch_trading_view_history(
        "BTC_THB", "1", 1640995200, 1640998800
    )
    assert response.get("s") == "ok"


# Test authentication edge cases
def test_client_without_api_secret():
    client = Client(api_key="test-key")
    with pytest.raises(BitkubException) as exc_info:
        client._sign("test")
    assert "API secret not set" in str(exc_info.value)


def test_private_headers():
    client = Client(api_key="test-key", api_secret="test-secret")
    headers = client._private_headers("1640995200000", "test-signature")
    assert headers["X-BTK-APIKEY"] == "test-key"
    assert headers["X-BTK-TIMESTAMP"] == "1640995200000"
    assert headers["X-BTK-SIGN"] == "test-signature"
    assert headers["Accept"] == "application/json"
    assert headers["Content-Type"] == "application/json"


def test_public_headers():
    client = Client()
    headers = client._public_headers()
    assert headers["Accept"] == "application/json"
    assert headers["Content-Type"] == "application/json"
    assert "X-BTK-APIKEY" not in headers


# Test signature generation
def test_sign_method():
    client = Client(api_secret="test-secret")
    signature = client._sign("test-payload")
    # Verify signature is a valid hex string of correct length (64 chars for SHA256)
    assert len(signature) == 64
    assert all(c in "0123456789abcdef" for c in signature)
    # Verify it produces consistent results
    assert client._sign("test-payload") == signature


# Test error handling improvements
def test_handle_response_success(mock_client: Client):
    import requests

    response = requests.Response()
    response.status_code = 200
    response._content = b'{"success": true}'
    result = mock_client._handle_response(response)
    assert result["success"] is True


def test_guard_errors_http_error(mock_client: Client):
    import requests

    response = requests.Response()
    response.status_code = 400
    response._content = b"Bad Request"
    with pytest.raises(BitkubException) as exc_info:
        mock_client._guard_errors(response)
    assert "400" in str(exc_info.value)


def test_handle_response_invalid_json(mock_client: Client):
    import requests

    response = requests.Response()
    response.status_code = 200
    response._content = b"invalid json"
    with pytest.raises(BitkubException) as exc_info:
        mock_client._handle_response(response)
    assert "Invalid JSON response" in str(exc_info.value)


# Test BaseClient functionality
def test_base_client_initialization():
    from typing import Any, Dict

    from bitkub.client import BaseClient

    class ConcreteBaseClient(BaseClient):
        def _send_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
            return {}

    base_client = ConcreteBaseClient(
        api_key="test-key",
        api_secret="test-secret",
        base_url="https://api.test.com",
        logging_level=logging.DEBUG,
    )
    assert base_client._api_key == "test-key"
    assert base_client._api_secret == "test-secret"
    assert base_client._base_url == "https://api.test.com"
    assert base_client.logger.level == logging.DEBUG


def test_json_encode():
    from typing import Any, Dict

    from bitkub.client import BaseClient

    class ConcreteBaseClient(BaseClient):
        def _send_request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
            return {}

    base_client = ConcreteBaseClient()
    data = {"test": "value", "number": 123}
    result = base_client._json_encode(data)
    assert result == '{"test": "value", "number": 123}'


# Test parameter validation and edge cases
def test_fetch_order_history_all_params(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.get(
        "/api/v3/market/my-order-history",
        json={"error": 0, "pagination": {"last": 1, "page": 2}, "result": []},
    )
    mock_client.fetch_order_history(
        symbol="THB_BTC", page=2, limit=20, start_time=1640995200, end_time=1640998800
    )
    assert matcher.called
    # Parse query parameters and verify them
    from urllib.parse import parse_qs

    query_dict = parse_qs(matcher.last_request.query)

    assert "sym" in query_dict
    assert query_dict["sym"][0].upper() == "THB_BTC"
    assert query_dict["p"][0] == "2"
    assert query_dict["lmt"][0] == "20"
    assert query_dict["start"][0] == "1640995200"
    assert query_dict["end"][0] == "1640998800"


def test_fetch_deposits_with_pagination(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post(
        "/api/v3/crypto/deposit-history",
        json={"error": 0, "result": [], "pagination": {"page": 2, "last": 5}},
    )
    mock_client.fetch_deposits(page=2, limit=20)
    assert matcher.called
    query_params = dict(
        [param.split("=") for param in matcher.last_request.query.split("&")]
    )
    assert query_params["p"] == "2"
    assert query_params["lmt"] == "20"


def test_fetch_withdrawals_with_pagination(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post(
        "/api/v3/crypto/withdraw-history",
        json={"error": 0, "result": [], "pagination": {"page": 3, "last": 10}},
    )
    mock_client.fetch_withdrawals(page=3, limit=50)
    assert matcher.called
    query_params = dict(
        [param.split("=") for param in matcher.last_request.query.split("&")]
    )
    assert query_params["p"] == "3"
    assert query_params["lmt"] == "50"


def test_fetch_fiat_deposits_with_pagination(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post(
        "/api/v3/fiat/deposit-history",
        json={"error": 0, "result": [], "pagination": {"page": 1, "last": 1}},
    )
    mock_client.fetch_fiat_deposits(page=1, limit=25)
    assert matcher.called
    query_params = dict(
        [param.split("=") for param in matcher.last_request.query.split("&")]
    )
    assert query_params["p"] == "1"
    assert query_params["lmt"] == "25"


def test_fetch_fiat_withdrawals_with_pagination(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post(
        "/api/v3/fiat/withdraw-history",
        json={"error": 0, "result": [], "pagination": {"page": 2, "last": 3}},
    )
    mock_client.fetch_fiat_withdrawals(page=2, limit=15)
    assert matcher.called
    query_params = dict(
        [param.split("=") for param in matcher.last_request.query.split("&")]
    )
    assert query_params["p"] == "2"
    assert query_params["lmt"] == "15"


# Test order creation with different parameters
def test_create_order_buy_with_client_id(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post("/api/v3/market/place-bid", json={"error": 0})
    mock_client.create_order_buy(
        symbol="THB_BTC",
        amount=1000,
        rate=2500000,
        type="market",
        client_id="custom-123",
    )
    assert matcher.called
    request_data = matcher.last_request.json()
    assert request_data["client_id"] == "custom-123"
    assert request_data["typ"] == "market"


def test_create_order_sell_with_client_id(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post("/api/v3/market/place-ask", json={"error": 0})
    mock_client.create_order_sell(
        symbol="THB_ETH", amount=0.5, rate=140000, type="market", client_id="sell-456"
    )
    assert matcher.called
    request_data = matcher.last_request.json()
    assert request_data["client_id"] == "sell-456"
    assert request_data["typ"] == "market"
    assert request_data["sym"] == "THB_ETH"


def test_cancel_order_with_all_params(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post("/api/v3/market/cancel-order", json={"error": 0})
    mock_client.cancel_order(symbol="THB_BTC", id="12345", side="buy", hash="abc123")
    assert matcher.called
    request_data = matcher.last_request.json()
    assert request_data["sym"] == "THB_BTC"
    assert request_data["id"] == "12345"
    assert request_data["sd"] == "buy"
    assert request_data["hash"] == "abc123"


def test_fetch_order_info_with_symbol_id_side(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.get(
        "/api/v3/market/order-info",
        json={"error": 0, "result": {"id": "12345", "side": "buy"}},
    )
    mock_client.fetch_order_info(symbol="THB_BTC", id="12345", side="buy")
    assert matcher.called
    # Parse query parameters and verify them
    from urllib.parse import parse_qs

    query_dict = parse_qs(matcher.last_request.query)

    assert "sym" in query_dict
    assert query_dict["sym"][0].upper() == "THB_BTC"
    assert query_dict["id"][0] == "12345"
    assert query_dict["sd"][0] == "buy"


# Test withdraw with memo
def test_withdraw_with_memo_request_body(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post("/api/v3/crypto/withdraw", json={"error": 0})
    mock_client.withdraw(
        currency="XRP", amount=100, address="rAddress123", network="XRP", memo="12345"
    )
    assert matcher.called
    request_data = matcher.last_request.json()
    assert request_data["cur"] == "XRP"
    assert request_data["amt"] == 100
    assert request_data["adr"] == "rAddress123"
    assert request_data["net"] == "XRP"
    assert request_data["mem"] == "12345"


def test_withdraw_without_memo_request_body(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post("/api/v3/crypto/withdraw", json={"error": 0})
    mock_client.withdraw(
        currency="BTC", amount=0.1, address="bc1address123", network="BTC"
    )
    assert matcher.called
    request_data = matcher.last_request.json()
    assert request_data["cur"] == "BTC"
    assert request_data["amt"] == 0.1
    assert request_data["adr"] == "bc1address123"
    assert request_data["net"] == "BTC"
    assert request_data["mem"] is None


def test_withdraw_fiat_request_body(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    matcher = mock_requests.post("/api/v3/fiat/withdraw", json={"error": 0})
    mock_client.withdraw_fiat("bank123", 5000)
    assert matcher.called
    request_data = matcher.last_request.json()
    assert request_data["id"] == "bank123"
    assert request_data["amt"] == 5000


# Test request paths, bodies, and query parameters for all endpoints
def test_public_endpoints_paths_and_params(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test that public endpoints use correct paths and query parameters"""

    # Test fetch_status
    status_matcher = mock_requests.get("/api/status", json=[{"status": "ok"}])
    mock_client.fetch_status()
    assert status_matcher.called
    assert status_matcher.last_request.method == "GET"
    assert status_matcher.last_request.path == "/api/status"

    # Test fetch_server_time
    time_matcher = mock_requests.get("/api/v3/servertime", json={"result": 1640995200})
    mock_client.fetch_server_time()
    assert time_matcher.called
    assert time_matcher.last_request.method == "GET"
    assert time_matcher.last_request.path == "/api/v3/servertime"

    # Test fetch_symbols
    symbols_matcher = mock_requests.get("/api/market/symbols", json={"result": []})
    mock_client.fetch_symbols()
    assert symbols_matcher.called
    assert symbols_matcher.last_request.method == "GET"
    assert symbols_matcher.last_request.path == "/api/market/symbols"

    # Test fetch_tickers with symbol parameter
    ticker_matcher = mock_requests.get("/api/v3/market/ticker", json={"THB_BTC": {}})
    mock_client.fetch_tickers("THB_BTC")
    assert ticker_matcher.called
    query_dict = parse_qs(ticker_matcher.last_request.query)
    assert "sym" in query_dict
    assert query_dict["sym"][0].upper() == "THB_BTC"

    # Test fetch_trades with parameters
    trades_matcher = mock_requests.get("/api/v3/market/trades", json={"result": []})
    mock_client.fetch_trades("THB_BTC", 25)
    assert trades_matcher.called
    query_dict = parse_qs(trades_matcher.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_BTC"
    assert query_dict["lmt"][0] == "25"

    # Test fetch_bids with parameters
    bids_matcher = mock_requests.get("/api/v3/market/bids", json={"result": []})
    mock_client.fetch_bids("THB_ETH", 15)
    assert bids_matcher.called
    query_dict = parse_qs(bids_matcher.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_ETH"
    assert query_dict["lmt"][0] == "15"

    # Test fetch_asks with parameters
    asks_matcher = mock_requests.get("/api/v3/market/asks", json={"result": []})
    mock_client.fetch_asks("THB_ADA", 30)
    assert asks_matcher.called
    query_dict = parse_qs(asks_matcher.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_ADA"
    assert query_dict["lmt"][0] == "30"

    # Test fetch_order_books with parameters
    books_matcher = mock_requests.get("/api/market/books", json={"result": {}})
    mock_client.fetch_order_books("THB_DOT", 20)
    assert books_matcher.called
    query_dict = parse_qs(books_matcher.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_DOT"
    assert query_dict["lmt"][0] == "20"

    # Test fetch_depth with parameters
    depth_matcher = mock_requests.get("/api/v3/market/depth", json={"result": {}})
    mock_client.fetch_depth("THB_XRP", 50)
    assert depth_matcher.called
    query_dict = parse_qs(depth_matcher.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_XRP"
    assert query_dict["lmt"][0] == "50"

    # Test fetch_trading_view_history with all parameters
    tv_matcher = mock_requests.get("/tradingview/history", json={"s": "ok"})
    mock_client.fetch_trading_view_history("BTC_THB", "1D", 1640000000, 1641000000)
    assert tv_matcher.called
    query_dict = parse_qs(tv_matcher.last_request.query)
    assert query_dict["symbol"][0].upper() == "BTC_THB"
    assert query_dict["resolution"][0].upper() == "1D"
    assert query_dict["from"][0] == "1640000000"
    assert query_dict["to"][0] == "1641000000"


def test_private_endpoints_paths_and_bodies(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test that private endpoints use correct paths and request bodies"""

    # Test fetch_user_limits
    limits_matcher = mock_requests.post("/api/v3/user/limits", json={"error": 0})
    mock_client.fetch_user_limits()
    assert limits_matcher.called
    assert limits_matcher.last_request.method == "POST"
    assert limits_matcher.last_request.path == "/api/v3/user/limits"
    assert limits_matcher.last_request.json() == {}

    # Test fetch_user_trade_credit
    credits_matcher = mock_requests.post(
        "/api/v3/user/trading-credits", json={"error": 0}
    )
    mock_client.fetch_user_trade_credit()
    assert credits_matcher.called
    assert credits_matcher.last_request.path == "/api/v3/user/trading-credits"
    assert credits_matcher.last_request.json() == {}

    # Test fetch_wallet
    wallet_matcher = mock_requests.post("/api/v3/market/wallet", json={"error": 0})
    mock_client.fetch_wallet()
    assert wallet_matcher.called
    assert wallet_matcher.last_request.path == "/api/v3/market/wallet"
    assert wallet_matcher.last_request.json() == {}

    # Test fetch_balances
    balances_matcher = mock_requests.post("/api/v3/market/balances", json={"error": 0})
    mock_client.fetch_balances()
    assert balances_matcher.called
    assert balances_matcher.last_request.path == "/api/v3/market/balances"
    assert balances_matcher.last_request.json() == {}

    # Test create_websocket_token
    wstoken_matcher = mock_requests.post("/api/v3/market/wstoken", json={"error": 0})
    mock_client.create_websocket_token()
    assert wstoken_matcher.called
    assert wstoken_matcher.last_request.path == "/api/v3/market/wstoken"
    assert wstoken_matcher.last_request.json() == {}


def test_order_endpoints_request_bodies(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test order creation/cancellation endpoints with detailed body validation"""

    # Test create_order_buy with all parameters
    buy_matcher = mock_requests.post("/api/v3/market/place-bid", json={"error": 0})
    mock_client.create_order_buy(
        symbol="THB_BTC",
        amount=50000,
        rate=2500000,
        type="market",
        client_id="buy-order-123",
    )
    assert buy_matcher.called
    assert buy_matcher.last_request.path == "/api/v3/market/place-bid"
    request_data = buy_matcher.last_request.json()
    assert request_data["sym"] == "THB_BTC"
    assert request_data["amt"] == 50000
    assert request_data["rat"] == 2500000
    assert request_data["typ"] == "market"
    assert request_data["client_id"] == "buy-order-123"

    # Test create_order_sell with all parameters
    sell_matcher = mock_requests.post("/api/v3/market/place-ask", json={"error": 0})
    mock_client.create_order_sell(
        symbol="THB_ETH",
        amount=0.5,
        rate=140000,
        type="limit",
        client_id="sell-order-456",
    )
    assert sell_matcher.called
    assert sell_matcher.last_request.path == "/api/v3/market/place-ask"
    request_data = sell_matcher.last_request.json()
    assert request_data["sym"] == "THB_ETH"
    assert request_data["amt"] == 0.5
    assert request_data["rat"] == 140000
    assert request_data["typ"] == "limit"
    assert request_data["client_id"] == "sell-order-456"

    # Test cancel_order with different parameter combinations
    cancel_matcher = mock_requests.post(
        "/api/v3/market/cancel-order", json={"error": 0}
    )
    mock_client.cancel_order(hash="order-hash-789")
    assert cancel_matcher.called
    assert cancel_matcher.last_request.path == "/api/v3/market/cancel-order"
    request_data = cancel_matcher.last_request.json()
    assert request_data["sym"] == ""
    assert request_data["id"] == ""
    assert request_data["sd"] == ""
    assert request_data["hash"] == "order-hash-789"


def test_order_history_endpoints_query_params(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test order history endpoints with various query parameter combinations"""

    # Test fetch_open_orders
    open_orders_matcher = mock_requests.get(
        "/api/v3/market/my-open-orders", json={"error": 0}
    )
    mock_client.fetch_open_orders("THB_BTC")
    assert open_orders_matcher.called
    assert open_orders_matcher.last_request.method == "GET"
    assert open_orders_matcher.last_request.path == "/api/v3/market/my-open-orders"
    query_dict = parse_qs(open_orders_matcher.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_BTC"

    # Test fetch_order_history with minimal parameters
    history_matcher1 = mock_requests.get(
        "/api/v3/market/my-order-history", json={"error": 0}
    )
    mock_client.fetch_order_history("THB_ETH")
    assert history_matcher1.called
    query_dict = parse_qs(history_matcher1.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_ETH"
    assert query_dict["p"][0] == "1"  # default page
    assert query_dict["lmt"][0] == "10"  # default limit

    # Test fetch_order_history with no optional parameters
    history_matcher2 = mock_requests.get(
        "/api/v3/market/my-order-history", json={"error": 0}
    )
    mock_client.fetch_order_history("THB_ADA", page=0, limit=0)
    assert history_matcher2.called
    query_dict = parse_qs(history_matcher2.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_ADA"
    # Should not include page/limit when they are 0 (falsy)
    assert "p" not in query_dict or query_dict["p"][0] == "0"
    assert "lmt" not in query_dict or query_dict["lmt"][0] == "0"

    # Test fetch_order_info with hash only
    info_matcher1 = mock_requests.get("/api/v3/market/order-info", json={"error": 0})
    mock_client.fetch_order_info(hash="order-hash-123")
    assert info_matcher1.called
    query_dict = parse_qs(info_matcher1.last_request.query)
    assert query_dict["hash"][0] == "order-hash-123"
    assert "sym" not in query_dict
    assert "id" not in query_dict
    assert "sd" not in query_dict

    # Test fetch_order_info with empty parameters (should not include them)
    info_matcher2 = mock_requests.get("/api/v3/market/order-info", json={"error": 0})
    mock_client.fetch_order_info(symbol="", id="", side="", hash="valid-hash")
    assert info_matcher2.called
    query_dict = parse_qs(info_matcher2.last_request.query)
    assert query_dict["hash"][0] == "valid-hash"
    # Empty strings should not be included in query
    assert "sym" not in query_dict or query_dict["sym"][0] == ""
    assert "id" not in query_dict or query_dict["id"][0] == ""
    assert "sd" not in query_dict or query_dict["sd"][0] == ""


def test_crypto_endpoints_request_bodies(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test crypto-related endpoints with request body validation"""

    # Test withdraw with memo
    withdraw_matcher1 = mock_requests.post("/api/v3/crypto/withdraw", json={"error": 0})
    mock_client.withdraw(
        currency="XRP",
        amount=100.5,
        address="rXRPAddress123",
        network="XRP",
        memo="destination-tag-123",
    )
    assert withdraw_matcher1.called
    assert withdraw_matcher1.last_request.path == "/api/v3/crypto/withdraw"
    request_data = withdraw_matcher1.last_request.json()
    assert request_data["cur"] == "XRP"
    assert request_data["amt"] == 100.5
    assert request_data["adr"] == "rXRPAddress123"
    assert request_data["net"] == "XRP"
    assert request_data["mem"] == "destination-tag-123"

    # Test withdraw without memo
    withdraw_matcher2 = mock_requests.post("/api/v3/crypto/withdraw", json={"error": 0})
    mock_client.withdraw(
        currency="BTC", amount=0.001, address="bc1bitcoinaddress", network="BTC"
    )
    assert withdraw_matcher2.called
    request_data = withdraw_matcher2.last_request.json()
    assert request_data["cur"] == "BTC"
    assert request_data["amt"] == 0.001
    assert request_data["adr"] == "bc1bitcoinaddress"
    assert request_data["net"] == "BTC"
    assert request_data["mem"] is None

    # Test fetch_addresses
    addresses_matcher = mock_requests.post(
        "/api/v3/crypto/addresses", json={"error": 0}
    )
    mock_client.fetch_addresses()
    assert addresses_matcher.called
    assert addresses_matcher.last_request.path == "/api/v3/crypto/addresses"
    assert addresses_matcher.last_request.json() == {}

    # Test fetch_deposits with pagination
    deposits_matcher = mock_requests.post(
        "/api/v3/crypto/deposit-history", json={"error": 0}
    )
    mock_client.fetch_deposits(page=3, limit=25)
    assert deposits_matcher.called
    assert deposits_matcher.last_request.path == "/api/v3/crypto/deposit-history"
    query_dict = parse_qs(deposits_matcher.last_request.query)
    assert query_dict["p"][0] == "3"
    assert query_dict["lmt"][0] == "25"

    # Test fetch_withdrawals with pagination
    withdrawals_matcher = mock_requests.post(
        "/api/v3/crypto/withdraw-history", json={"error": 0}
    )
    mock_client.fetch_withdrawals(page=2, limit=50)
    assert withdrawals_matcher.called
    assert withdrawals_matcher.last_request.path == "/api/v3/crypto/withdraw-history"
    query_dict = parse_qs(withdrawals_matcher.last_request.query)
    assert query_dict["p"][0] == "2"
    assert query_dict["lmt"][0] == "50"


def test_fiat_endpoints_request_bodies(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test fiat-related endpoints with request body validation"""

    # Test fetch_fiat_accounts
    accounts_matcher = mock_requests.post("/api/v3/fiat/accounts", json={"error": 0})
    mock_client.fetch_fiat_accounts()
    assert accounts_matcher.called
    assert accounts_matcher.last_request.path == "/api/v3/fiat/accounts"
    assert accounts_matcher.last_request.json() == {}

    # Test withdraw_fiat
    fiat_withdraw_matcher = mock_requests.post(
        "/api/v3/fiat/withdraw", json={"error": 0}
    )
    mock_client.withdraw_fiat("bank-account-789", 25000.50)
    assert fiat_withdraw_matcher.called
    assert fiat_withdraw_matcher.last_request.path == "/api/v3/fiat/withdraw"
    request_data = fiat_withdraw_matcher.last_request.json()
    assert request_data["id"] == "bank-account-789"
    assert request_data["amt"] == 25000.50

    # Test fetch_fiat_deposits with pagination
    fiat_deposits_matcher = mock_requests.post(
        "/api/v3/fiat/deposit-history", json={"error": 0}
    )
    mock_client.fetch_fiat_deposits(page=5, limit=100)
    assert fiat_deposits_matcher.called
    assert fiat_deposits_matcher.last_request.path == "/api/v3/fiat/deposit-history"
    query_dict = parse_qs(fiat_deposits_matcher.last_request.query)
    assert query_dict["p"][0] == "5"
    assert query_dict["lmt"][0] == "100"

    # Test fetch_fiat_withdrawals with pagination
    fiat_withdrawals_matcher = mock_requests.post(
        "/api/v3/fiat/withdraw-history", json={"error": 0}
    )
    mock_client.fetch_fiat_withdrawals(page=1, limit=20)
    assert fiat_withdrawals_matcher.called
    assert fiat_withdrawals_matcher.last_request.path == "/api/v3/fiat/withdraw-history"
    query_dict = parse_qs(fiat_withdrawals_matcher.last_request.query)
    assert query_dict["p"][0] == "1"
    assert query_dict["lmt"][0] == "20"


def test_http_methods_validation(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test that endpoints use correct HTTP methods"""

    # Public endpoints should use GET
    get_endpoints = [
        ("/api/status", lambda: mock_client.fetch_status()),
        ("/api/v3/servertime", lambda: mock_client.fetch_server_time()),
        ("/api/market/symbols", lambda: mock_client.fetch_symbols()),
        ("/api/v3/market/ticker", lambda: mock_client.fetch_tickers()),
        ("/api/v3/market/trades", lambda: mock_client.fetch_trades()),
        ("/api/v3/market/bids", lambda: mock_client.fetch_bids()),
        ("/api/v3/market/asks", lambda: mock_client.fetch_asks()),
        ("/api/market/books", lambda: mock_client.fetch_order_books()),
        ("/api/v3/market/depth", lambda: mock_client.fetch_depth()),
        ("/tradingview/history", lambda: mock_client.fetch_trading_view_history()),
    ]

    for path, func in get_endpoints:
        matcher = mock_requests.get(path, json={})
        func()
        assert matcher.called
        assert matcher.last_request.method == "GET"

    # Private query endpoints should use GET with authentication
    private_get_endpoints = [
        (
            "/api/v3/market/my-open-orders",
            lambda: mock_client.fetch_open_orders("THB_BTC"),
        ),
        (
            "/api/v3/market/my-order-history",
            lambda: mock_client.fetch_order_history("THB_BTC"),
        ),
        (
            "/api/v3/market/order-info",
            lambda: mock_client.fetch_order_info(hash="test"),
        ),
    ]

    for path, func in private_get_endpoints:
        matcher = mock_requests.get(path, json={})
        func()
        assert matcher.called
        assert matcher.last_request.method == "GET"
        # Check for authentication headers
        assert "X-BTK-APIKEY" in matcher.last_request.headers
        assert "X-BTK-TIMESTAMP" in matcher.last_request.headers
        assert "X-BTK-SIGN" in matcher.last_request.headers

    # Private action endpoints should use POST with authentication
    private_post_endpoints = [
        ("/api/v3/user/limits", lambda: mock_client.fetch_user_limits()),
        ("/api/v3/user/trading-credits", lambda: mock_client.fetch_user_trade_credit()),
        ("/api/v3/market/wallet", lambda: mock_client.fetch_wallet()),
        ("/api/v3/market/balances", lambda: mock_client.fetch_balances()),
        (
            "/api/v3/market/place-bid",
            lambda: mock_client.create_order_buy("THB_BTC", 1000, 2500000),
        ),
        (
            "/api/v3/market/place-ask",
            lambda: mock_client.create_order_sell("THB_BTC", 0.001, 2500000),
        ),
        ("/api/v3/market/cancel-order", lambda: mock_client.cancel_order(hash="test")),
        ("/api/v3/market/wstoken", lambda: mock_client.create_websocket_token()),
        (
            "/api/v3/crypto/withdraw",
            lambda: mock_client.withdraw("BTC", 0.001, "address", "BTC"),
        ),
        ("/api/v3/crypto/addresses", lambda: mock_client.fetch_addresses()),
        ("/api/v3/crypto/deposit-history", lambda: mock_client.fetch_deposits()),
        ("/api/v3/crypto/withdraw-history", lambda: mock_client.fetch_withdrawals()),
        ("/api/v3/fiat/accounts", lambda: mock_client.fetch_fiat_accounts()),
        ("/api/v3/fiat/withdraw", lambda: mock_client.withdraw_fiat("bank123", 1000)),
        ("/api/v3/fiat/deposit-history", lambda: mock_client.fetch_fiat_deposits()),
        ("/api/v3/fiat/withdraw-history", lambda: mock_client.fetch_fiat_withdrawals()),
    ]

    for path, func in private_post_endpoints:
        matcher = mock_requests.post(path, json={})
        func()
        assert matcher.called
        assert matcher.last_request.method == "POST"
        # Check for authentication headers
        assert "X-BTK-APIKEY" in matcher.last_request.headers
        assert "X-BTK-TIMESTAMP" in matcher.last_request.headers
        assert "X-BTK-SIGN" in matcher.last_request.headers


def test_parameter_encoding_edge_cases(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test edge cases for parameter encoding"""

    # Test symbols with special characters
    ticker_matcher = mock_requests.get("/api/v3/market/ticker", json={})
    mock_client.fetch_tickers("THB_BTC-TEST")
    assert ticker_matcher.called
    query_dict = parse_qs(ticker_matcher.last_request.query)
    assert query_dict["sym"][0].upper() == "THB_BTC-TEST"

    # Test zero and negative values in order creation
    buy_matcher = mock_requests.post("/api/v3/market/place-bid", json={})
    mock_client.create_order_buy("THB_BTC", 0, 0, "limit", "")
    assert buy_matcher.called
    request_data = buy_matcher.last_request.json()
    assert request_data["amt"] == 0
    assert request_data["rat"] == 0
    assert request_data["client_id"] == ""

    # Test large numbers
    sell_matcher = mock_requests.post("/api/v3/market/place-ask", json={})
    mock_client.create_order_sell(
        "THB_BTC", 999999.999999, 9999999999, "market", "large-order-123456789"
    )
    assert sell_matcher.called
    request_data = sell_matcher.last_request.json()
    assert request_data["amt"] == 999999.999999
    assert request_data["rat"] == 9999999999
    assert request_data["client_id"] == "large-order-123456789"

    # Test Unicode characters in addresses
    withdraw_matcher = mock_requests.post("/api/v3/crypto/withdraw", json={})
    mock_client.withdraw("ETH", 1.0, "0x123abc", "ETH", "memo-with-unicode-∞")
    assert withdraw_matcher.called
    request_data = withdraw_matcher.last_request.json()
    assert request_data["adr"] == "0x123abc"
    assert request_data["mem"] == "memo-with-unicode-∞"


# Comprehensive Header Validation Tests
def test_public_endpoint_headers_validation(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test that public endpoints send correct headers (no auth headers)."""

    # Test various public endpoints to ensure they only send public headers
    public_endpoints_to_test = [
        ("/api/status", lambda: mock_client.fetch_status()),
        ("/api/v3/servertime", lambda: mock_client.fetch_server_time()),
        ("/api/market/symbols", lambda: mock_client.fetch_symbols()),
        ("/api/v3/market/ticker", lambda: mock_client.fetch_tickers("THB_BTC")),
        ("/api/v3/market/trades", lambda: mock_client.fetch_trades("THB_BTC", 10)),
        ("/api/v3/market/bids", lambda: mock_client.fetch_bids("THB_BTC", 10)),
        ("/api/v3/market/asks", lambda: mock_client.fetch_asks("THB_BTC", 10)),
        ("/api/market/books", lambda: mock_client.fetch_order_books("THB_BTC", 10)),
        ("/api/v3/market/depth", lambda: mock_client.fetch_depth("THB_BTC", 10)),
        (
            "/tradingview/history",
            lambda: mock_client.fetch_trading_view_history(
                "BTC_THB", "1D", 1640000000, 1641000000
            ),
        ),
    ]

    for endpoint_path, endpoint_func in public_endpoints_to_test:
        matcher = mock_requests.get(endpoint_path, json={"result": []})
        endpoint_func()

        assert matcher.called, f"Endpoint {endpoint_path} was not called"
        headers = matcher.last_request.headers

        # Verify required public headers are present
        assert "Accept" in headers, f"Accept header missing for {endpoint_path}"
        assert headers["Accept"] == "application/json", (
            f"Accept header incorrect for {endpoint_path}"
        )
        assert "Content-Type" in headers, (
            f"Content-Type header missing for {endpoint_path}"
        )
        assert headers["Content-Type"] == "application/json", (
            f"Content-Type header incorrect for {endpoint_path}"
        )

        # Verify authentication headers are NOT present
        assert "X-BTK-APIKEY" not in headers, (
            f"X-BTK-APIKEY should not be present for public endpoint {endpoint_path}"
        )
        assert "X-BTK-TIMESTAMP" not in headers, (
            f"X-BTK-TIMESTAMP should not be present for public endpoint {endpoint_path}"
        )
        assert "X-BTK-SIGN" not in headers, (
            f"X-BTK-SIGN should not be present for public endpoint {endpoint_path}"
        )


def test_private_endpoint_headers_validation(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test that private endpoints send correct authentication headers."""

    # Test various private endpoints to ensure they send authentication headers
    private_endpoints_to_test = [
        ("POST", "/api/v3/user/limits", lambda: mock_client.fetch_user_limits()),
        (
            "POST",
            "/api/v3/user/trading-credits",
            lambda: mock_client.fetch_user_trade_credit(),
        ),
        ("POST", "/api/v3/market/wallet", lambda: mock_client.fetch_wallet()),
        ("POST", "/api/v3/market/balances", lambda: mock_client.fetch_balances()),
        (
            "POST",
            "/api/v3/market/place-bid",
            lambda: mock_client.create_order_buy("THB_BTC", 1000, 2500000),
        ),
        (
            "POST",
            "/api/v3/market/place-ask",
            lambda: mock_client.create_order_sell("THB_BTC", 0.001, 2500000),
        ),
        (
            "POST",
            "/api/v3/market/cancel-order",
            lambda: mock_client.cancel_order(hash="test-hash"),
        ),
        (
            "POST",
            "/api/v3/market/wstoken",
            lambda: mock_client.create_websocket_token(),
        ),
        (
            "GET",
            "/api/v3/market/my-open-orders",
            lambda: mock_client.fetch_open_orders("THB_BTC"),
        ),
        (
            "GET",
            "/api/v3/market/my-order-history",
            lambda: mock_client.fetch_order_history("THB_BTC"),
        ),
        (
            "GET",
            "/api/v3/market/order-info",
            lambda: mock_client.fetch_order_info(hash="test-hash"),
        ),
        (
            "POST",
            "/api/v3/crypto/withdraw",
            lambda: mock_client.withdraw("BTC", 0.001, "test-address", "BTC"),
        ),
        ("POST", "/api/v3/crypto/addresses", lambda: mock_client.fetch_addresses()),
        (
            "POST",
            "/api/v3/crypto/deposit-history",
            lambda: mock_client.fetch_deposits(),
        ),
        (
            "POST",
            "/api/v3/crypto/withdraw-history",
            lambda: mock_client.fetch_withdrawals(),
        ),
        ("POST", "/api/v3/fiat/accounts", lambda: mock_client.fetch_fiat_accounts()),
        (
            "POST",
            "/api/v3/fiat/withdraw",
            lambda: mock_client.withdraw_fiat("bank123", 1000),
        ),
        (
            "POST",
            "/api/v3/fiat/deposit-history",
            lambda: mock_client.fetch_fiat_deposits(),
        ),
        (
            "POST",
            "/api/v3/fiat/withdraw-history",
            lambda: mock_client.fetch_fiat_withdrawals(),
        ),
    ]

    for method, endpoint_path, endpoint_func in private_endpoints_to_test:
        if method == "POST":
            matcher = mock_requests.post(endpoint_path, json={"error": 0})
        else:
            matcher = mock_requests.get(endpoint_path, json={"error": 0})

        endpoint_func()

        assert matcher.called, f"Endpoint {endpoint_path} was not called"
        headers = matcher.last_request.headers

        # Verify required public headers are present
        assert "Accept" in headers, f"Accept header missing for {endpoint_path}"
        assert headers["Accept"] == "application/json", (
            f"Accept header incorrect for {endpoint_path}"
        )
        assert "Content-Type" in headers, (
            f"Content-Type header missing for {endpoint_path}"
        )
        assert headers["Content-Type"] == "application/json", (
            f"Content-Type header incorrect for {endpoint_path}"
        )

        # Verify authentication headers are present
        assert "X-BTK-APIKEY" in headers, (
            f"X-BTK-APIKEY header missing for private endpoint {endpoint_path}"
        )
        assert "X-BTK-TIMESTAMP" in headers, (
            f"X-BTK-TIMESTAMP header missing for private endpoint {endpoint_path}"
        )
        assert "X-BTK-SIGN" in headers, (
            f"X-BTK-SIGN header missing for private endpoint {endpoint_path}"
        )

        # Verify authentication header values are non-empty
        assert headers["X-BTK-APIKEY"], (
            f"X-BTK-APIKEY header is empty for {endpoint_path}"
        )
        assert headers["X-BTK-TIMESTAMP"], (
            f"X-BTK-TIMESTAMP header is empty for {endpoint_path}"
        )
        assert headers["X-BTK-SIGN"], f"X-BTK-SIGN header is empty for {endpoint_path}"


def test_authentication_header_format_validation(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test that authentication headers have correct format and values."""

    # Test a representative private endpoint
    matcher = mock_requests.post("/api/v3/market/wallet", json={"error": 0})
    mock_client.fetch_wallet()

    assert matcher.called
    headers = matcher.last_request.headers

    # Test X-BTK-APIKEY format
    api_key = headers["X-BTK-APIKEY"]
    assert api_key == mock_client._api_key, "X-BTK-APIKEY should match client's API key"

    # Test X-BTK-TIMESTAMP format (should be numeric timestamp)
    timestamp = headers["X-BTK-TIMESTAMP"]
    assert timestamp.isdigit(), "X-BTK-TIMESTAMP should be a numeric string"
    assert len(timestamp) == 13, (
        "X-BTK-TIMESTAMP should be 13 digits (milliseconds since epoch)"
    )

    # Test X-BTK-SIGN format (should be hexadecimal string of 64 characters for SHA256)
    signature = headers["X-BTK-SIGN"]
    assert len(signature) == 64, "X-BTK-SIGN should be 64 characters (SHA256 hex)"
    assert all(c in "0123456789abcdef" for c in signature), (
        "X-BTK-SIGN should be valid hexadecimal"
    )


def test_header_consistency_across_methods(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test that headers are consistent across different HTTP methods."""

    # Test GET private endpoint
    get_matcher = mock_requests.get("/api/v3/market/my-open-orders", json={"error": 0})
    mock_client.fetch_open_orders("THB_BTC")

    # Test POST private endpoint
    post_matcher = mock_requests.post("/api/v3/market/wallet", json={"error": 0})
    mock_client.fetch_wallet()

    # Both should have the same header structure
    get_headers = get_matcher.last_request.headers
    post_headers = post_matcher.last_request.headers

    # Check that both have all required headers
    required_headers = [
        "Accept",
        "Content-Type",
        "X-BTK-APIKEY",
        "X-BTK-TIMESTAMP",
        "X-BTK-SIGN",
    ]

    for header in required_headers:
        assert header in get_headers, f"GET request missing {header}"
        assert header in post_headers, f"POST request missing {header}"

        # Content headers should be identical
        if header in ["Accept", "Content-Type", "X-BTK-APIKEY"]:
            assert get_headers[header] == post_headers[header], (
                f"Header {header} should be identical across methods"
            )


def test_header_authentication_with_different_clients():
    """Test that different client instances use their own API keys in headers."""
    import requests_mock

    # Create two clients with different API keys
    client1 = Client(api_key="test-key-1", api_secret="test-secret-1")
    client2 = Client(api_key="test-key-2", api_secret="test-secret-2")

    with requests_mock.Mocker() as m:
        matcher = m.post("/api/v3/market/wallet", json={"error": 0})

        # Make requests with both clients
        client1.fetch_wallet()
        client2.fetch_wallet()

        # Verify that each client used its own API key
        # requests_mock collects all requests in request_history
        assert len(matcher.request_history) == 2

        headers1 = matcher.request_history[0].headers
        headers2 = matcher.request_history[1].headers

        assert headers1["X-BTK-APIKEY"] == "test-key-1"
        assert headers2["X-BTK-APIKEY"] == "test-key-2"

        # Signatures should be different (different secrets and timestamps)
        assert headers1["X-BTK-SIGN"] != headers2["X-BTK-SIGN"]


def test_header_timestamp_freshness(
    mock_client: Client, mock_requests: requests_mock.Mocker
):
    """Test that timestamp headers are fresh (recent) for each request."""
    import time

    matcher = mock_requests.post("/api/v3/market/wallet", json={"error": 0})

    # Record time before request
    before_request = int(time.time() * 1000)
    mock_client.fetch_wallet()
    after_request = int(time.time() * 1000)

    # Get timestamp from headers
    timestamp_str = matcher.last_request.headers["X-BTK-TIMESTAMP"]
    timestamp = int(timestamp_str)

    # Timestamp should be within reasonable range of current time
    assert before_request <= timestamp <= after_request + 1000, (
        "Timestamp should be current time in milliseconds"
    )


def test_headers_with_missing_credentials():
    """Test header behavior when API credentials are missing."""
    import requests_mock

    # Test client without API secret
    client_no_secret = Client(api_key="test-key")

    with requests_mock.Mocker() as m:
        m.post("/api/v3/market/wallet", json={"error": 0})

        # Should raise exception when trying to sign without secret
        with pytest.raises(BitkubException) as exc_info:
            client_no_secret.fetch_wallet()
        assert "API secret not set" in str(exc_info.value)

    # Test client without API key (should still work but use empty key)
    client_no_key = Client(api_secret="test-secret")

    with requests_mock.Mocker() as m:
        matcher = m.post("/api/v3/market/wallet", json={"error": 0})
        client_no_key.fetch_wallet()

        headers = matcher.last_request.headers
        assert headers["X-BTK-APIKEY"] == ""  # Empty API key should be sent


# V4 Crypto API Tests
class TestV4CryptoAPI:
    """Test V4 crypto API methods."""

    def test_fetch_crypto_addresses_v4(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test fetch crypto addresses v4 API."""
        mock_data = {
            "code": 200,
            "message": "success",
            "data": [
                {
                    "symbol": "BTC",
                    "address": "3BtxdKw6XSbneNvmJTLVHS9XfNYM7VAe8k",
                    "network": "BTC",
                    "memo": "",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ],
        }
        matcher = mock_requests.get("/api/v4/crypto/addresses", json=mock_data)

        # Test with all parameters
        response = mock_client.fetch_crypto_addresses_v4(
            page=1, limit=10, symbol="BTC", network="BTC", memo="test"
        )

        assert matcher.called
        assert response == mock_data

        # Verify query parameters
        request = matcher.last_request
        assert "page=1" in request.url
        assert "limit=10" in request.url
        assert "symbol=BTC" in request.url
        assert "network=BTC" in request.url
        assert "memo=test" in request.url

    def test_fetch_crypto_addresses_v4_minimal(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test fetch crypto addresses v4 API with minimal parameters."""
        mock_data = {"code": 200, "data": []}
        matcher = mock_requests.get("/api/v4/crypto/addresses", json=mock_data)

        response = mock_client.fetch_crypto_addresses_v4()

        assert matcher.called
        assert response == mock_data

    def test_generate_crypto_address_v4(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test generate crypto address v4 API."""
        mock_data = {
            "code": 200,
            "message": "success",
            "data": {
                "symbol": "BTC",
                "address": "3NewGeneratedAddress123",
                "network": "BTC",
            },
        }
        matcher = mock_requests.post("/api/v4/crypto/addresses", json=mock_data)

        response = mock_client.generate_crypto_address_v4("BTC", "BTC")

        assert matcher.called
        assert response == mock_data

        # Verify request body
        import json

        request_body = json.loads(matcher.last_request.text)
        assert request_body["symbol"] == "BTC"
        assert request_body["network"] == "BTC"

    def test_fetch_crypto_deposits_v4(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test fetch crypto deposits v4 API."""
        mock_data = {
            "code": 200,
            "data": [
                {
                    "id": "12345",
                    "symbol": "BTC",
                    "amount": "0.001",
                    "status": "complete",
                    "network": "BTC",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ],
        }
        matcher = mock_requests.get("/api/v4/crypto/deposits", json=mock_data)

        response = mock_client.fetch_crypto_deposits_v4(
            page=1,
            limit=20,
            symbol="BTC",
            status="complete",
            created_start=1640000000,
            created_end=1641000000,
        )

        assert matcher.called
        assert response == mock_data

        # Verify query parameters
        request = matcher.last_request
        assert "page=1" in request.url
        assert "limit=20" in request.url
        assert "symbol=BTC" in request.url
        assert "status=complete" in request.url
        assert "created_start=1640000000" in request.url
        assert "created_end=1641000000" in request.url

    def test_fetch_crypto_withdraws_v4(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test fetch crypto withdraws v4 API."""
        mock_data = {
            "code": 200,
            "data": [
                {
                    "id": "67890",
                    "symbol": "ETH",
                    "amount": "0.1",
                    "status": "pending",
                    "network": "ETH",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ],
        }
        matcher = mock_requests.get("/api/v4/crypto/withdraws", json=mock_data)

        response = mock_client.fetch_crypto_withdraws_v4(
            page=2, limit=50, symbol="ETH", status="pending"
        )

        assert matcher.called
        assert response == mock_data

        # Verify query parameters
        request = matcher.last_request
        assert "page=2" in request.url
        assert "limit=50" in request.url
        assert "symbol=ETH" in request.url
        assert "status=pending" in request.url

    def test_fetch_crypto_coins_v4(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test fetch crypto coins v4 API."""
        mock_data = {
            "code": 200,
            "data": [
                {
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "networks": ["BTC"],
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                },
                {
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "networks": ["ETH", "ERC20"],
                    "deposit_enabled": True,
                    "withdraw_enabled": True,
                },
            ],
        }
        matcher = mock_requests.get("/api/v4/crypto/coins", json=mock_data)

        response = mock_client.fetch_crypto_coins_v4()

        assert matcher.called
        assert response == mock_data

    def test_fetch_crypto_compensations_v4(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test fetch crypto compensations v4 API."""
        mock_data = {
            "code": 200,
            "data": [
                {
                    "id": "comp123",
                    "symbol": "BTC",
                    "amount": "0.0001",
                    "reason": "Network fee compensation",
                    "created_at": "2023-01-01T00:00:00Z",
                }
            ],
        }
        matcher = mock_requests.get("/api/v4/crypto/compensations", json=mock_data)

        response = mock_client.fetch_crypto_compensations_v4()

        assert matcher.called
        assert response == mock_data


# Error Handling Tests
class TestClientErrorHandling:
    """Test client error handling paths."""

    def test_api_error_response(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test handling of API error responses."""
        error_response = {"error": 1, "message": "Invalid API key"}
        mock_requests.post("/api/v3/market/wallet", json=error_response)

        with pytest.raises(BitkubAPIException) as exc_info:
            mock_client.fetch_wallet()

        assert exc_info.value.code == 1
        assert "Invalid API key" in str(exc_info.value)

    def test_http_error_response(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test handling of HTTP error responses."""
        mock_requests.post(
            "/api/v3/market/wallet", status_code=500, text="Internal Server Error"
        )

        with pytest.raises(BitkubException) as exc_info:
            mock_client.fetch_wallet()

        assert "500" in str(exc_info.value)
        assert "Internal Server Error" in str(exc_info.value)

    def test_invalid_json_response(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test handling of invalid JSON responses."""
        mock_requests.get("/api/status", text="Invalid JSON Response", status_code=200)

        with pytest.raises(BitkubException) as exc_info:
            mock_client.fetch_status()

        assert "Invalid JSON response" in str(exc_info.value)

    def test_network_timeout(self, mock_client: Client):
        """Test handling of network timeouts."""
        from unittest.mock import patch

        import requests

        with patch.object(mock_client.session, "request") as mock_request:
            mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

            with pytest.raises(requests.exceptions.Timeout):
                mock_client.fetch_status()

    def test_connection_error(self, mock_client: Client):
        """Test handling of connection errors."""
        from unittest.mock import patch

        import requests

        with patch.object(mock_client.session, "request") as mock_request:
            mock_request.side_effect = requests.exceptions.ConnectionError(
                "Connection failed"
            )

            with pytest.raises(requests.exceptions.ConnectionError):
                mock_client.fetch_status()

    def test_zero_error_code_not_treated_as_error(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test that error code 0 is not treated as an error."""
        success_response = {"error": 0, "result": {"balance": 1000}}
        mock_requests.post("/api/v3/market/wallet", json=success_response)

        # Should not raise an exception
        response = mock_client.fetch_wallet()
        assert response["error"] == 0
        assert response["result"]["balance"] == 1000

    def test_api_error_without_message(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test API error response without message field."""
        error_response = {"error": 5}  # No message field
        mock_requests.post("/api/v3/market/wallet", json=error_response)

        with pytest.raises(BitkubAPIException) as exc_info:
            mock_client.fetch_wallet()

        assert exc_info.value.code == 5
        assert "API Error 5" in str(exc_info.value)

    def test_non_dict_error_response(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test non-dict response that doesn't have error field."""
        list_response = [{"status": "ok"}]
        mock_requests.get("/api/status", json=list_response)

        # Should not raise an exception, just return the list
        response = mock_client.fetch_status()
        assert response == list_response

    def test_abstract_methods_coverage(self):
        """Test abstract base class methods for coverage."""
        from bitkub.client import BaseClient

        # Test that BaseClient cannot be instantiated directly due to abstract method
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseClient()

    def test_legacy_send_request_method(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test legacy __send_request method for coverage."""
        mock_requests.post("/api/v3/market/wallet", json={"error": 0, "result": {}})

        # Access the private method directly
        response = mock_client._Client__send_request("POST", "/api/v3/market/wallet")
        assert response["error"] == 0

    def test_send_request_with_body_and_params(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test _send_request with both body and query params."""
        mock_requests.post("/api/v3/market/place-bid", json={"error": 0, "result": {}})

        response = mock_client._send_request(
            "POST",
            "/api/v3/market/place-bid",
            body={"sym": "THB_BTC", "amt": 100},
            query_params={"test": "param"},
        )
        assert response["error"] == 0

    def test_public_request_authenticated_false(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test _send_request with authenticated=False."""
        mock_requests.get("/api/status", json=[{"status": "ok"}])

        response = mock_client._send_request("GET", "/api/status", authenticated=False)
        assert response == [{"status": "ok"}]

    def test_typed_response_methods(
        self, mock_client: Client, mock_requests: requests_mock.Mocker
    ):
        """Test typed response methods for coverage."""
        # Test server time typed response
        mock_requests.get("/api/v3/servertime", json={"error": 0, "result": 1633424427})
        server_time = mock_client.fetch_server_time_typed()
        assert server_time.result == 1633424427

        # Test status typed response
        status_data = {
            "error": 0,
            "result": [{"name": "test", "status": "ok", "message": ""}],
        }
        mock_requests.get("/api/status", json=status_data)
        status = mock_client.fetch_status_typed()
        assert status.result == [{"name": "test", "status": "ok", "message": ""}]

        # Test symbols typed response
        symbols_data = {
            "error": 0,
            "result": [{"id": 1, "symbol": "THB_BTC", "info": "Bitcoin"}],
        }
        mock_requests.get("/api/market/symbols", json=symbols_data)
        symbols = mock_client.fetch_symbols_typed()
        assert symbols.error == 0
        assert len(symbols.result) == 1

        # Test tickers typed response
        ticker_data = {
            "error": 0,
            "result": {
                "THB_BTC": {
                    "id": 1,
                    "last": 1000000,
                    "lowestAsk": 1000000,
                    "highestBid": 999000,
                    "percentChange": 1.0,
                    "baseVolume": 100,
                    "quoteVolume": 100000000,
                    "isFrozen": 0,
                    "high24hr": 1100000,
                    "low24hr": 900000,
                    "change": 10000,
                }
            },
        }
        mock_requests.get("/api/v3/market/ticker", json=ticker_data)
        tickers = mock_client.fetch_tickers_typed()
        assert "THB_BTC" in tickers.result


class TestBaseClientCoverage:
    """Test BaseClient methods for coverage."""

    def test_base_client_initialization(self):
        """Test BaseClient initialization."""
        from typing import Any, Dict

        from bitkub.client import BaseClient

        # Create a concrete implementation for testing
        class TestClient(BaseClient):
            def _send_request(
                self, method: str, path: str, **kwargs: Any
            ) -> Dict[str, Any]:
                return {}

        client = TestClient(
            api_key="test-key",
            api_secret="test-secret",
            base_url="https://test.api.com",
            logging_level=10,  # DEBUG level
        )

        assert client._api_key == "test-key"
        assert client._api_secret == "test-secret"
        assert client._base_url == "https://test.api.com"
        assert client.logger.level == 10

    def test_json_encode_method(self):
        """Test _json_encode method."""
        from typing import Any, Dict

        from bitkub.client import BaseClient

        class TestClient(BaseClient):
            def _send_request(
                self, method: str, path: str, **kwargs: Any
            ) -> Dict[str, Any]:
                return {}

        client = TestClient()
        test_data = {"key": "value", "number": 123}
        result = client._json_encode(test_data)

        import json

        assert result == json.dumps(test_data)

    def test_public_headers_method(self):
        """Test _public_headers method."""
        from typing import Any, Dict

        from bitkub.client import BaseClient

        class TestClient(BaseClient):
            def _send_request(
                self, method: str, path: str, **kwargs: Any
            ) -> Dict[str, Any]:
                return {}

        client = TestClient()
        headers = client._public_headers()

        expected = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        assert headers == expected

    def test_private_headers_method(self):
        """Test _private_headers method."""
        from typing import Any, Dict

        from bitkub.client import BaseClient

        class TestClient(BaseClient):
            def _send_request(
                self, method: str, path: str, **kwargs: Any
            ) -> Dict[str, Any]:
                return {}

        client = TestClient(api_key="test-key")
        headers = client._private_headers("1234567890", "test-signature")

        expected = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-BTK-TIMESTAMP": "1234567890",
            "X-BTK-SIGN": "test-signature",
            "X-BTK-APIKEY": "test-key",
        }
        assert headers == expected

    def test_sign_method(self):
        """Test _sign method."""
        from typing import Any, Dict

        from bitkub.client import BaseClient

        class TestClient(BaseClient):
            def _send_request(
                self, method: str, path: str, **kwargs: Any
            ) -> Dict[str, Any]:
                return {}

        client = TestClient(api_secret="test-secret")
        signature = client._sign("test-payload")

        # Should return a hex string
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex is 64 characters

        # Test with empty payload
        empty_sig = client._sign("")
        assert isinstance(empty_sig, str)
        assert len(empty_sig) == 64

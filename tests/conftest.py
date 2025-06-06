# fixture
import pytest
import requests_mock


@pytest.fixture
def input_value():
    input = 39
    return input


@pytest.fixture
def mock_requests():
    with requests_mock.Mocker() as mock:
        yield mock


@pytest.fixture
def mock_client(mock_requests):
    import logging

    from bitkub import Client

    client = Client(api_key="api-key", api_secret="api-secret")

    logger = logging.getLogger("bitkub")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    return client


@pytest.fixture
def with_request_status_ok(mock_requests):
    mock_requests.get(
        "/api/status",
        json=[
            {"name": "Non-secure endpoints", "status": "ok", "message": ""},
            {"name": "Secure endpoints", "status": "ok", "message": ""},
        ],
    )


@pytest.fixture
def with_request_status_error(mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/status",
        json={"error": "Invalid API key"},
        status_code=400,
    )


@pytest.fixture
def with_request_status_invalid_json(mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/status",
        text="Invalid JSON",
        status_code=200,
    )


@pytest.fixture
def with_request_tickers(mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/v3/market/ticker",
        json={
            "THB_BTC": {
                "id": 1,
                "last": 2418999.8,
                "lowestAsk": 2418999.8,
                "highestBid": 2416599.78,
                "percentChange": 1,
                "baseVolume": 215.23564897,
                "quoteVolume": 518727096.21,
                "isFrozen": 0,
                "high24hr": 2459000,
                "low24hr": 2370000.01,
                "change": 23999.81,
                "prevClose": 2418999.8,
                "prevOpen": 2394999.99,
            },
            "THB_ETH": {
                "id": 2,
                "last": 138931.8,
                "lowestAsk": 138968.55,
                "highestBid": 138854.6,
                "percentChange": 1.89,
                "baseVolume": 2137.55285235,
                "quoteVolume": 297780227.04,
                "isFrozen": 0,
                "high24hr": 142000,
                "low24hr": 136303.47,
                "change": 2577.6,
                "prevClose": 138931.8,
                "prevOpen": 136354.2,
            },
        },
    )


@pytest.fixture
def with_request_user_limits(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/user/limits",
        json={
            "error": 0,
            "result": {
                "limits": {
                    "crypto": {"deposit": 2.06711509, "withdraw": 2.06711509},
                    "fiat": {"deposit": 5000000, "withdraw": 5000000},
                },
                "usage": {
                    "crypto": {
                        "deposit": 1.3926524,
                        "withdraw": 0.97573785,
                        "deposit_percentage": 67.37,
                        "withdraw_percentage": 47.2,
                        "deposit_thb_equivalent": 3368589.4,
                        "withdraw_thb_equivalent": 2360143.98,
                    },
                    "fiat": {
                        "deposit": 0,
                        "withdraw": 0,
                        "deposit_percentage": 0,
                        "withdraw_percentage": 0,
                    },
                },
                "rate": 2418830,
            },
        },
    )


@pytest.fixture
def with_request_user_trade_credit(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/user/trading-credits",
        json={"error": 0, "result": 1000},
    )


@pytest.fixture
def with_create_order_buy(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/market/place-bid",
        json={
            "error": 0,
            "result": {
                "id": "54583082",
                "hash": "fwQ6dnQWTQMygWR3HsiAatTK1B6",
                "typ": "market",
                "amt": 10,
                "rat": 0,
                "fee": 0,
                "cre": 0,
                "rec": 0,
                "ts": "1710179754",
            },
        },
    )


@pytest.fixture
def with_create_order_sell(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/market/place-ask",
        json={
            "error": 0,
            "result": {
                "id": "54583082",
                "hash": "fwQ6dnQWTQMygWR3HsiAatTK1B6",
                "typ": "market",
                "amt": 10,
                "rat": 0,
                "fee": 0,
                "cre": 0,
                "rec": 0,
                "ts": "1710179754",
            },
        },
    )


@pytest.fixture
def with_fetch_open_order_success(mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/v3/market/my-open-orders?sym=THB_BTC",
        json={
            "error": 0,
            "result": [
                {
                    "id": "22810019",
                    "hash": "234234230s",
                    "side": "sell",
                    "type": "limit",
                    "rate": "40",
                    "fee": "0.1",
                    "credit": "0.1",
                    "amount": "1",
                    "receive": "40",
                    "parent_id": "0",
                    "super_id": "0",
                    "client_id": "",
                    "ts": 1657464464000,
                }
            ],
        },
    )


@pytest.fixture
def with_fetch_order_history_success(mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/v3/market/my-order-history?sym=THB_BTC",
        json={
            "error": 0,
            "pagination": {"last": 1, "page": 1},
            "result": [
                {
                    "txn_id": "BTCSELL00230234023",
                    "order_id": "23423423",
                    "hash": "flskxmsofjsdfos",
                    "parent_order_id": "0",
                    "parent_order_hash": "flskxmsofjsdfos112",
                    "super_order_id": "0",
                    "super_order_hash": "flskxmsofjsdfos112",
                    "client_id": "",
                    "taken_by_me": False,
                    "is_maker": False,
                    "side": "sell",
                    "type": "market",
                    "rate": "2431000",
                    "fee": "6.08",
                    "credit": "0",
                    "amount": "0.001",
                    "ts": 1709911962336,
                }
            ],
        },
    )


@pytest.fixture
def with_withdraw_success(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/crypto/withdraw",
        json={
            "error": 0,
            "result": {
                "txn": "KKKWD0007382474",
                "adr": "A667355",
                "mem": "",
                "cur": "KKK",
                "net": "KKK",
                "amt": 10,
                "fee": 0.02,
                "ts": 1710443913,
            },
        },
    )


@pytest.fixture
def with_fetch_addresses_success(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/crypto/addresses",
        json={
            "error": 0,
            "result": [
                {
                    "currency": "BTC",
                    "address": "3BtxdKw6XSbneNvmJTLVHS9XfNYM7VAe8k",
                    "tag": 0,
                    "time": 1570893867,
                }
            ],
            "pagination": {"page": 1, "last": 1},
        },
    )


@pytest.fixture
def with_fetch_withdrawals_success(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/crypto/withdraw-history",
        json={
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
                    "time": 1570893493,
                }
            ],
            "pagination": {"page": 1, "last": 1},
        },
    )


@pytest.fixture
def with_fetch_deposits_success(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/crypto/deposit-history",
        json={
            "error": 0,
            "result": [
                {
                    "txn_id": "THBDP0000012345",
                    "currency": "THB",
                    "amount": 5000.55,
                    "status": "complete",
                    "time": 1570893867,
                }
            ],
            "pagination": {"page": 1, "last": 1},
        },
    )


@pytest.fixture
def with_fetch_fiat_accounts_success(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/fiat/accounts",
        json={
            "error": 0,
            "result": [
                {
                    "id": "7262109099",
                    "bank": "Kasikorn Bank",
                    "name": "Somsak",
                    "time": 1570893867,
                }
            ],
            "pagination": {"page": 1, "last": 1},
        },
    )


@pytest.fixture
def with_withdraw_fiat_success(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/fiat/withdraw",
        json={
            "error": 0,
            "result": {
                "txn": "THBWD0000012345",
                "acc": "7262109099",
                "cur": "THB",
                "amt": 21,
                "fee": 20,
                "rec": 1,
                "ts": 1569999999,
            },
        },
    )


@pytest.fixture
def with_fetch_fiat_withdrawals_success(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/fiat/withdraw-history",
        json={
            "error": 0,
            "result": [
                {
                    "txn_id": "THBWD0000012345",
                    "currency": "THB",
                    "amount": "21",
                    "fee": 20,
                    "status": "complete",
                    "time": 1570893493,
                }
            ],
            "pagination": {"page": 1, "last": 1},
        },
    )


@pytest.fixture
def with_fetch_fiat_deposits_success(mock_requests: requests_mock.Mocker):
    mock_requests.post(
        "/api/v3/fiat/deposit-history",
        json={
            "error": 0,
            "result": [
                {
                    "txn_id": "THBDP0000012345",
                    "currency": "THB",
                    "amount": 5000.55,
                    "status": "complete",
                    "time": 1570893867,
                }
            ],
            "pagination": {"page": 1, "last": 1},
        },
    )

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
    from bitkub import Client
    import logging

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
        "/api/market/ticker",
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

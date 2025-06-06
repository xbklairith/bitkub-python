import pytest

from bitkub import const as c


def test_http_methods():
    assert c.GET == "GET"
    assert c.POST == "POST"
    assert c.DELETE == "DELETE"


def test_endpoints_dataclass_frozen():
    endpoints = c.Endpoints()

    # Test that the dataclass is frozen (immutable)
    with pytest.raises(AttributeError):
        endpoints.STATUS = "/different/path"


def test_public_endpoints():
    endpoints = c.Endpoints()

    # Test public endpoints
    assert endpoints.STATUS == "/api/status"
    assert endpoints.MARKET_SYMBOLS == "/api/market/symbols"
    assert endpoints.MARKET_TICKER == "/api/v3/market/ticker"
    assert endpoints.MARKET_TRADES == "/api/v3/market/trades"
    assert endpoints.MARKET_BIDS == "/api/v3/market/bids"
    assert endpoints.MARKET_ASKS == "/api/v3/market/asks"
    assert endpoints.MARKET_BOOKS == "/api/market/books"
    assert endpoints.MARKET_DEPTH == "/api/v3/market/depth"
    assert endpoints.TRADING_VIEW_HISTORY == "/tradingview/history"
    assert endpoints.SERVER_TIME == "/api/v3/servertime"


def test_private_user_endpoints():
    endpoints = c.Endpoints()

    # Test private user endpoints
    assert endpoints.USER_LIMITS == "/api/v3/user/limits"
    assert endpoints.USER_TRADING_CREDITS == "/api/v3/user/trading-credits"


def test_private_market_endpoints():
    endpoints = c.Endpoints()

    # Test private market endpoints
    assert endpoints.MARKET_WALLET == "/api/v3/market/wallet"
    assert endpoints.MARKET_BALANCES == "/api/v3/market/balances"
    assert endpoints.MARKET_PLACE_BID == "/api/v3/market/place-bid"
    assert endpoints.MARKET_PLACE_ASK == "/api/v3/market/place-ask"
    assert endpoints.MARKET_CANCEL_ORDER == "/api/v3/market/cancel-order"
    assert endpoints.MARKET_WSTOKEN == "/api/v3/market/wstoken"
    assert endpoints.MARKET_MY_OPEN_ORDERS == "/api/v3/market/my-open-orders"
    assert endpoints.MARKET_MY_ORDER_HISTORY == "/api/v3/market/my-order-history"
    assert endpoints.MARKET_ORDER_INFO == "/api/v3/market/order-info"


def test_crypto_endpoints():
    endpoints = c.Endpoints()

    # Test crypto endpoints
    assert endpoints.CRYPTO_INTERNAL_WITHDRAW == "/api/v3/crypto/internal-withdraw"
    assert endpoints.CRYPTO_ADDRESSES == "/api/v3/crypto/addresses"
    assert endpoints.CRYPTO_WITHDRAW == "/api/v3/crypto/withdraw"
    assert endpoints.CRYPTO_DEPOSIT_HISTORY == "/api/v3/crypto/deposit-history"
    assert endpoints.CRYPTO_WITHDRAW_HISTORY == "/api/v3/crypto/withdraw-history"
    assert endpoints.CRYPTO_GENERATE_ADDRESS == "/api/v3/crypto/generate-address"


def test_fiat_endpoints():
    endpoints = c.Endpoints()

    # Test fiat endpoints
    assert endpoints.FIAT_ACCOUNTS == "/api/v3/fiat/accounts"
    assert endpoints.FIAT_WITHDRAW == "/api/v3/fiat/withdraw"
    assert endpoints.FIAT_DEPOSIT_HISTORY == "/api/v3/fiat/deposit-history"
    assert endpoints.FIAT_WITHDRAW_HISTORY == "/api/v3/fiat/withdraw-history"


def test_endpoints_instance_creation():
    endpoints1 = c.Endpoints()
    endpoints2 = c.Endpoints()

    # Both instances should have the same values
    assert endpoints1.STATUS == endpoints2.STATUS
    assert endpoints1.MARKET_TICKER == endpoints2.MARKET_TICKER


def test_all_endpoints_are_strings():
    endpoints = c.Endpoints()

    # Get all endpoint attributes
    endpoint_attrs = [attr for attr in dir(endpoints) if not attr.startswith("_")]

    for attr_name in endpoint_attrs:
        endpoint_value = getattr(endpoints, attr_name)
        assert isinstance(endpoint_value, str), f"{attr_name} should be a string"
        assert endpoint_value.startswith("/"), f"{attr_name} should start with '/'"


def test_endpoints_versioning_consistency():
    endpoints = c.Endpoints()

    # Test that v3 endpoints are consistently versioned
    v3_endpoints = [
        endpoints.SERVER_TIME,
        endpoints.USER_LIMITS,
        endpoints.USER_TRADING_CREDITS,
        endpoints.MARKET_WALLET,
        endpoints.MARKET_BALANCES,
        endpoints.MARKET_PLACE_BID,
        endpoints.MARKET_PLACE_ASK,
        endpoints.MARKET_CANCEL_ORDER,
        endpoints.MARKET_WSTOKEN,
        endpoints.MARKET_MY_OPEN_ORDERS,
        endpoints.MARKET_MY_ORDER_HISTORY,
        endpoints.MARKET_ORDER_INFO,
        endpoints.CRYPTO_INTERNAL_WITHDRAW,
        endpoints.CRYPTO_ADDRESSES,
        endpoints.CRYPTO_WITHDRAW,
        endpoints.CRYPTO_DEPOSIT_HISTORY,
        endpoints.CRYPTO_WITHDRAW_HISTORY,
        endpoints.CRYPTO_GENERATE_ADDRESS,
        endpoints.FIAT_ACCOUNTS,
        endpoints.FIAT_WITHDRAW,
        endpoints.FIAT_DEPOSIT_HISTORY,
        endpoints.FIAT_WITHDRAW_HISTORY,
    ]

    for endpoint in v3_endpoints:
        assert "/api/v3/" in endpoint, f"Endpoint {endpoint} should contain '/api/v3/'"


def test_non_v3_endpoints():
    endpoints = c.Endpoints()

    # Test that some endpoints don't use v3 versioning (based on official API docs)
    non_v3_endpoints = [
        endpoints.STATUS,
        endpoints.MARKET_SYMBOLS,
        endpoints.MARKET_BOOKS,
        endpoints.TRADING_VIEW_HISTORY,
    ]

    for endpoint in non_v3_endpoints:
        assert "/api/v3/" not in endpoint, (
            f"Endpoint {endpoint} should not contain '/api/v3/'"
        )

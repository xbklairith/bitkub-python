from dataclasses import dataclass

GET = "GET"
POST = "POST"
DELETE = "DELETE"


@dataclass(frozen=True)
class Endpoints:
    # public endpoints
    STATUS = "/api/status"
    MARKET_SYMBOLS = "/api/market/symbols"
    MARKET_TICKER = "/api/v3/market/ticker"
    MARKET_TRADES = "/api/v3/market/trades"
    MARKET_BIDS = "/api/v3/market/bids"
    MARKET_ASKS = "/api/v3/market/asks"
    MARKET_BOOKS = "/api/market/books"
    MARKET_DEPTH = "/api/v3/market/depth"
    TRADING_VIEW_HISTORY = "/tradingview/history"
    SERVER_TIME = "/api/v3/servertime"

    # private endpoints

    USER_LIMITS = "/api/v3/user/limits"
    USER_TRADING_CREDITS = "/api/v3/user/trading-credits"
    MARKET_WALLET = "/api/v3/market/wallet"
    MARKET_BALANCES = "/api/v3/market/balances"

    MARKET_PLACE_BID = "/api/v3/market/place-bid"
    MARKET_PLACE_ASK = "/api/v3/market/place-ask"
    MARKET_CANCEL_ORDER = "/api/v3/market/cancel-order"
    MARKET_WSTOKEN = "/api/v3/market/wstoken"

    MARKET_MY_OPEN_ORDERS = "/api/v3/market/my-open-orders"
    MARKET_MY_ORDER_HISTORY = "/api/v3/market/my-order-history"
    MARKET_ORDER_INFO = "/api/v3/market/order-info"

    CRYPTO_INTERNAL_WITHDRAW = "/api/v3/crypto/internal-withdraw"
    CRYPTO_ADDRESSES = "/api/v3/crypto/addresses"
    CRYPTO_WITHDRAW = "/api/v3/crypto/withdraw"
    CRYPTO_DEPOSIT_HISTORY = "/api/v3/crypto/deposit-history"
    CRYPTO_WITHDRAW_HISTORY = "/api/v3/crypto/withdraw-history"
    CRYPTO_GENERATE_ADDRESS = "/api/v3/crypto/generate-address"

    # v4 crypto endpoints
    CRYPTO_V4_ADDRESSES = "/api/v4/crypto/addresses"
    CRYPTO_V4_DEPOSITS = "/api/v4/crypto/deposits"
    CRYPTO_V4_WITHDRAWS = "/api/v4/crypto/withdraws"
    CRYPTO_V4_COINS = "/api/v4/crypto/coins"
    CRYPTO_V4_COMPENSATIONS = "/api/v4/crypto/compensations"
    FIAT_ACCOUNTS = "/api/v3/fiat/accounts"
    FIAT_WITHDRAW = "/api/v3/fiat/withdraw"
    FIAT_DEPOSIT_HISTORY = "/api/v3/fiat/deposit-history"
    FIAT_WITHDRAW_HISTORY = "/api/v3/fiat/withdraw-history"

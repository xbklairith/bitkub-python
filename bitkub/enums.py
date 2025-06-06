"""Enums for Bitkub API constants."""

from enum import Enum


class OrderType(str, Enum):
    """Order types for trading."""

    LIMIT = "limit"
    MARKET = "market"


class OrderSide(str, Enum):
    """Order sides for trading."""

    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Order status values."""

    PENDING = "pending"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"


class TimeResolution(str, Enum):
    """Time resolutions for trading view history."""

    ONE_MINUTE = "1"
    FIVE_MINUTES = "5"
    FIFTEEN_MINUTES = "15"
    THIRTY_MINUTES = "30"
    ONE_HOUR = "60"
    FOUR_HOURS = "240"
    ONE_DAY = "1D"


class HTTPMethod(str, Enum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class TransactionStatus(str, Enum):
    """Transaction status values."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"

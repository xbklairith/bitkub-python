"""Input validation utilities for Bitkub API parameters."""

import re
from typing import Optional, Union

from bitkub.enums import OrderSide, OrderType
from bitkub.exception import BitkubException


def validate_symbol(symbol: Optional[str]) -> Optional[str]:
    """
    Validate trading symbol format.

    Args:
        symbol: Trading symbol in format 'BASE_QUOTE' (e.g., 'THB_BTC')

    Returns:
        Validated and normalized symbol

    Raises:
        BitkubException: If symbol format is invalid
    """
    if symbol is None:
        return None

    if not isinstance(symbol, str):
        raise BitkubException("Symbol must be a string")

    symbol = symbol.strip().upper()

    if not symbol:
        return None

    # Validate format manually
    if "_" not in symbol:
        raise BitkubException("Symbol must be in format 'BASE_QUOTE' (e.g., 'THB_BTC')")

    parts = symbol.split("_")
    if len(parts) != 2:
        raise BitkubException("Symbol must have exactly one underscore")

    base, quote = parts
    if not base or not quote:
        raise BitkubException("Both base and quote currencies must be non-empty")

    return symbol


def validate_amount(amount: Union[int, float], min_amount: float = 0.0) -> float:
    """
    Validate amount parameter.

    Args:
        amount: Amount to validate
        min_amount: Minimum allowed amount

    Returns:
        Validated amount as float

    Raises:
        BitkubException: If amount is invalid
    """
    if not isinstance(amount, (int, float)):
        raise BitkubException("Amount must be a number")

    amount = float(amount)

    if amount < 0:
        raise BitkubException("Amount cannot be negative")

    if amount < min_amount:
        raise BitkubException(f"Amount must be at least {min_amount}")

    return amount


def validate_rate(rate: Union[int, float]) -> float:
    """
    Validate rate parameter.

    Args:
        rate: Rate to validate

    Returns:
        Validated rate as float

    Raises:
        BitkubException: If rate is invalid
    """
    if not isinstance(rate, (int, float)):
        raise BitkubException("Rate must be a number")

    rate = float(rate)

    if rate <= 0:
        raise BitkubException("Rate must be positive")

    return rate


def validate_order_type(order_type: Union[str, OrderType]) -> str:
    """
    Validate order type.

    Args:
        order_type: Order type to validate

    Returns:
        Validated order type string

    Raises:
        BitkubException: If order type is invalid
    """
    if isinstance(order_type, OrderType):
        return order_type.value

    if not isinstance(order_type, str):
        raise BitkubException("Order type must be a string or OrderType enum")

    order_type = order_type.lower().strip()

    try:
        OrderType(order_type)
        return order_type
    except ValueError:
        valid_types = [t.value for t in OrderType]
        raise BitkubException(
            f"Invalid order type. Must be one of: {valid_types}"
        ) from None


def validate_order_side(side: Union[str, OrderSide]) -> str:
    """
    Validate order side.

    Args:
        side: Order side to validate

    Returns:
        Validated order side string

    Raises:
        BitkubException: If order side is invalid
    """
    if isinstance(side, OrderSide):
        return side.value

    if not isinstance(side, str):
        raise BitkubException("Order side must be a string or OrderSide enum")

    side = side.lower().strip()

    try:
        OrderSide(side)
        return side
    except ValueError:
        valid_sides = [s.value for s in OrderSide]
        raise BitkubException(
            f"Invalid order side. Must be one of: {valid_sides}"
        ) from None


def validate_limit(limit: Optional[int], max_limit: int = 1000) -> int:
    """
    Validate limit parameter.

    Args:
        limit: Limit to validate
        max_limit: Maximum allowed limit

    Returns:
        Validated limit

    Raises:
        BitkubException: If limit is invalid
    """
    if limit is None:
        return 10  # Default limit

    if not isinstance(limit, int):
        raise BitkubException("Limit must be an integer")

    if limit <= 0:
        raise BitkubException("Limit must be positive")

    if limit > max_limit:
        raise BitkubException(f"Limit cannot exceed {max_limit}")

    return limit


def validate_page(page: Optional[int]) -> int:
    """
    Validate page parameter.

    Args:
        page: Page number to validate

    Returns:
        Validated page number

    Raises:
        BitkubException: If page is invalid
    """
    if page is None:
        return 1  # Default page

    if not isinstance(page, int):
        raise BitkubException("Page must be an integer")

    if page <= 0:
        raise BitkubException("Page must be positive")

    return page


def validate_timestamp(timestamp: Optional[int]) -> Optional[int]:
    """
    Validate timestamp parameter.

    Args:
        timestamp: Unix timestamp to validate

    Returns:
        Validated timestamp

    Raises:
        BitkubException: If timestamp is invalid
    """
    if timestamp is None:
        return None

    if not isinstance(timestamp, int):
        raise BitkubException("Timestamp must be an integer")

    if timestamp < 0:
        raise BitkubException("Timestamp cannot be negative")

    # Check if timestamp is reasonable (after 2000-01-01 and before 2100-01-01)
    if timestamp < 946684800 or timestamp > 4102444800:
        raise BitkubException("Timestamp appears to be invalid")

    return timestamp


def validate_address(address: str) -> str:
    """
    Validate cryptocurrency address.

    Args:
        address: Address to validate

    Returns:
        Validated address

    Raises:
        BitkubException: If address is invalid
    """
    if not isinstance(address, str):
        raise BitkubException("Address must be a string")

    address = address.strip()

    if not address:
        raise BitkubException("Address cannot be empty")

    # Basic format validation (addresses are typically alphanumeric)
    if not re.match(r"^[a-zA-Z0-9]+$", address):
        raise BitkubException("Address contains invalid characters")

    # Length validation (most crypto addresses are between 26-62 characters)
    if len(address) < 26 or len(address) > 62:
        raise BitkubException("Address length appears to be invalid")

    return address


def validate_currency(currency: str) -> str:
    """
    Validate currency code.

    Args:
        currency: Currency to validate

    Returns:
        Validated currency string

    Raises:
        BitkubException: If currency is invalid
    """
    if not isinstance(currency, str):
        raise BitkubException("Currency must be a string")

    currency = currency.upper().strip()

    if not currency:
        raise BitkubException("Currency cannot be empty")

    # Basic validation - currency codes are typically 3-4 characters
    if not re.match(r"^[A-Z]{2,5}$", currency):
        raise BitkubException("Invalid currency format")

    return currency


def validate_network(network: str) -> str:
    """
    Validate blockchain network.

    Args:
        network: Network to validate

    Returns:
        Validated network string

    Raises:
        BitkubException: If network is invalid
    """
    if not isinstance(network, str):
        raise BitkubException("Network must be a string")

    network = network.upper().strip()

    if not network:
        raise BitkubException("Network cannot be empty")

    return network


def validate_client_id(client_id: Optional[str]) -> Optional[str]:
    """
    Validate client ID.

    Args:
        client_id: Client ID to validate

    Returns:
        Validated client ID

    Raises:
        BitkubException: If client ID is invalid
    """
    if client_id is None or client_id == "":
        return None

    if not isinstance(client_id, str):
        raise BitkubException("Client ID must be a string")

    client_id = client_id.strip()

    if len(client_id) > 100:  # Arbitrary reasonable limit
        raise BitkubException("Client ID is too long")

    return client_id

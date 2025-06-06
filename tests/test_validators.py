"""Tests for validators module."""

import pytest

from bitkub.enums import OrderSide, OrderType
from bitkub.exception import BitkubException
from bitkub.validators import (
    validate_address,
    validate_amount,
    validate_client_id,
    validate_currency,
    validate_limit,
    validate_network,
    validate_order_side,
    validate_order_type,
    validate_page,
    validate_rate,
    validate_symbol,
    validate_timestamp,
)


class TestValidateSymbol:
    """Test validate_symbol function."""

    def test_valid_symbols(self):
        """Test valid symbol formats."""
        assert validate_symbol("THB_BTC") == "THB_BTC"
        assert validate_symbol("thb_btc") == "THB_BTC"
        assert validate_symbol("  THB_BTC  ") == "THB_BTC"
        assert validate_symbol("USDT_ETH") == "USDT_ETH"

    def test_none_symbol(self):
        """Test None symbol returns None."""
        assert validate_symbol(None) is None

    def test_empty_symbol(self):
        """Test empty symbol returns None."""
        assert validate_symbol("") is None
        assert validate_symbol("  ") is None

    def test_invalid_symbol_type(self):
        """Test invalid symbol type raises exception."""
        with pytest.raises(BitkubException, match="Symbol must be a string"):
            validate_symbol(123)

    def test_invalid_symbol_format(self):
        """Test invalid symbol formats raise exceptions."""
        with pytest.raises(BitkubException, match="Symbol must be in format"):
            validate_symbol("BTCTHB")

        with pytest.raises(
            BitkubException, match="Symbol must have exactly one underscore"
        ):
            validate_symbol("BTC_THB_USD")

        with pytest.raises(
            BitkubException, match="Both base and quote currencies must be non-empty"
        ):
            validate_symbol("_BTC")

        with pytest.raises(
            BitkubException, match="Both base and quote currencies must be non-empty"
        ):
            validate_symbol("THB_")


class TestValidateAmount:
    """Test validate_amount function."""

    def test_valid_amounts(self):
        """Test valid amounts."""
        assert validate_amount(10.5) == 10.5
        assert validate_amount(100) == 100.0
        assert validate_amount(0.1, min_amount=0.1) == 0.1

    def test_invalid_amount_type(self):
        """Test invalid amount type raises exception."""
        with pytest.raises(BitkubException, match="Amount must be a number"):
            validate_amount("invalid")

    def test_negative_amount(self):
        """Test negative amount raises exception."""
        with pytest.raises(BitkubException, match="Amount cannot be negative"):
            validate_amount(-10)

    def test_amount_below_minimum(self):
        """Test amount below minimum raises exception."""
        with pytest.raises(BitkubException, match="Amount must be at least 10"):
            validate_amount(5, min_amount=10)


class TestValidateRate:
    """Test validate_rate function."""

    def test_valid_rates(self):
        """Test valid rates."""
        assert validate_rate(1000.5) == 1000.5
        assert validate_rate(1) == 1.0

    def test_invalid_rate_type(self):
        """Test invalid rate type raises exception."""
        with pytest.raises(BitkubException, match="Rate must be a number"):
            validate_rate("invalid")

    def test_zero_or_negative_rate(self):
        """Test zero or negative rate raises exception."""
        with pytest.raises(BitkubException, match="Rate must be positive"):
            validate_rate(0)

        with pytest.raises(BitkubException, match="Rate must be positive"):
            validate_rate(-10)


class TestValidateOrderType:
    """Test validate_order_type function."""

    def test_valid_order_types(self):
        """Test valid order types."""
        assert validate_order_type("limit") == "limit"
        assert validate_order_type("market") == "market"
        assert validate_order_type("LIMIT") == "limit"
        assert validate_order_type("  limit  ") == "limit"

    def test_order_type_enum(self):
        """Test OrderType enum input."""
        assert validate_order_type(OrderType.LIMIT) == "limit"
        assert validate_order_type(OrderType.MARKET) == "market"

    def test_invalid_order_type(self):
        """Test invalid order type raises exception."""
        with pytest.raises(BitkubException, match="Order type must be a string"):
            validate_order_type(123)

        with pytest.raises(BitkubException, match="Invalid order type"):
            validate_order_type("invalid")


class TestValidateOrderSide:
    """Test validate_order_side function."""

    def test_valid_order_sides(self):
        """Test valid order sides."""
        assert validate_order_side("buy") == "buy"
        assert validate_order_side("sell") == "sell"
        assert validate_order_side("BUY") == "buy"
        assert validate_order_side("  sell  ") == "sell"

    def test_order_side_enum(self):
        """Test OrderSide enum input."""
        assert validate_order_side(OrderSide.BUY) == "buy"
        assert validate_order_side(OrderSide.SELL) == "sell"

    def test_invalid_order_side(self):
        """Test invalid order side raises exception."""
        with pytest.raises(BitkubException, match="Order side must be a string"):
            validate_order_side(123)

        with pytest.raises(BitkubException, match="Invalid order side"):
            validate_order_side("invalid")


class TestValidateLimit:
    """Test validate_limit function."""

    def test_valid_limits(self):
        """Test valid limits."""
        assert validate_limit(50) == 50
        assert validate_limit(None) == 10  # default
        assert validate_limit(1000, max_limit=1000) == 1000

    def test_invalid_limit_type(self):
        """Test invalid limit type raises exception."""
        with pytest.raises(BitkubException, match="Limit must be an integer"):
            validate_limit("invalid")

    def test_invalid_limit_values(self):
        """Test invalid limit values raise exceptions."""
        with pytest.raises(BitkubException, match="Limit must be positive"):
            validate_limit(0)

        with pytest.raises(BitkubException, match="Limit must be positive"):
            validate_limit(-10)

        with pytest.raises(BitkubException, match="Limit cannot exceed 100"):
            validate_limit(150, max_limit=100)


class TestValidatePage:
    """Test validate_page function."""

    def test_valid_pages(self):
        """Test valid page numbers."""
        assert validate_page(1) == 1
        assert validate_page(10) == 10
        assert validate_page(None) == 1  # default

    def test_invalid_page_type(self):
        """Test invalid page type raises exception."""
        with pytest.raises(BitkubException, match="Page must be an integer"):
            validate_page("invalid")

    def test_invalid_page_values(self):
        """Test invalid page values raise exceptions."""
        with pytest.raises(BitkubException, match="Page must be positive"):
            validate_page(0)

        with pytest.raises(BitkubException, match="Page must be positive"):
            validate_page(-1)


class TestValidateTimestamp:
    """Test validate_timestamp function."""

    def test_valid_timestamps(self):
        """Test valid timestamps."""
        assert validate_timestamp(1633424427) == 1633424427
        assert validate_timestamp(None) is None

    def test_invalid_timestamp_type(self):
        """Test invalid timestamp type raises exception."""
        with pytest.raises(BitkubException, match="Timestamp must be an integer"):
            validate_timestamp("invalid")

    def test_invalid_timestamp_values(self):
        """Test invalid timestamp values raise exceptions."""
        with pytest.raises(BitkubException, match="Timestamp cannot be negative"):
            validate_timestamp(-1)

        with pytest.raises(BitkubException, match="Timestamp appears to be invalid"):
            validate_timestamp(100)  # too old

        with pytest.raises(BitkubException, match="Timestamp appears to be invalid"):
            validate_timestamp(5000000000)  # too far in future


class TestValidateAddress:
    """Test validate_address function."""

    def test_valid_addresses(self):
        """Test valid crypto addresses."""
        # Bitcoin address
        btc_address = "3BtxdKw6XSbneNvmJTLVHS9XfNYM7VAe8k"
        assert validate_address(btc_address) == btc_address

        # Ethereum address (40 chars + 0x prefix, but we strip 0x)
        eth_address = "742d35Cc6675C88aa240E4c9b4EAAf1f8e0EF08A"
        assert validate_address(eth_address) == eth_address

    def test_invalid_address_type(self):
        """Test invalid address type raises exception."""
        with pytest.raises(BitkubException, match="Address must be a string"):
            validate_address(123)

    def test_invalid_address_values(self):
        """Test invalid address values raise exceptions."""
        with pytest.raises(BitkubException, match="Address cannot be empty"):
            validate_address("")

        with pytest.raises(BitkubException, match="Address cannot be empty"):
            validate_address("  ")

        with pytest.raises(
            BitkubException, match="Address contains invalid characters"
        ):
            validate_address("invalid@address!")

        with pytest.raises(
            BitkubException, match="Address length appears to be invalid"
        ):
            validate_address("short")

        with pytest.raises(
            BitkubException, match="Address length appears to be invalid"
        ):
            validate_address("a" * 70)  # too long


class TestValidateCurrency:
    """Test validate_currency function."""

    def test_valid_currencies(self):
        """Test valid currency codes."""
        assert validate_currency("BTC") == "BTC"
        assert validate_currency("btc") == "BTC"
        assert validate_currency("  eth  ") == "ETH"
        assert validate_currency("USDT") == "USDT"

    def test_invalid_currency_type(self):
        """Test invalid currency type raises exception."""
        with pytest.raises(BitkubException, match="Currency must be a string"):
            validate_currency(123)

    def test_invalid_currency_values(self):
        """Test invalid currency values raise exceptions."""
        with pytest.raises(BitkubException, match="Currency cannot be empty"):
            validate_currency("")

        with pytest.raises(BitkubException, match="Currency cannot be empty"):
            validate_currency("  ")

        with pytest.raises(BitkubException, match="Invalid currency format"):
            validate_currency("B")  # too short

        with pytest.raises(BitkubException, match="Invalid currency format"):
            validate_currency("TOOLONG")  # too long

        with pytest.raises(BitkubException, match="Invalid currency format"):
            validate_currency("BT1")  # contains number


class TestValidateNetwork:
    """Test validate_network function."""

    def test_valid_networks(self):
        """Test valid network names."""
        assert validate_network("BTC") == "BTC"
        assert validate_network("eth") == "ETH"
        assert validate_network("  polygon  ") == "POLYGON"

    def test_invalid_network_type(self):
        """Test invalid network type raises exception."""
        with pytest.raises(BitkubException, match="Network must be a string"):
            validate_network(123)

    def test_invalid_network_values(self):
        """Test invalid network values raise exceptions."""
        with pytest.raises(BitkubException, match="Network cannot be empty"):
            validate_network("")

        with pytest.raises(BitkubException, match="Network cannot be empty"):
            validate_network("  ")


class TestValidateClientId:
    """Test validate_client_id function."""

    def test_valid_client_ids(self):
        """Test valid client IDs."""
        assert validate_client_id("client123") == "client123"
        assert validate_client_id("  order-001  ") == "order-001"
        assert validate_client_id(None) is None
        assert validate_client_id("") is None

    def test_invalid_client_id_type(self):
        """Test invalid client ID type raises exception."""
        with pytest.raises(BitkubException, match="Client ID must be a string"):
            validate_client_id(123)

    def test_client_id_too_long(self):
        """Test client ID too long raises exception."""
        long_id = "a" * 101
        with pytest.raises(BitkubException, match="Client ID is too long"):
            validate_client_id(long_id)

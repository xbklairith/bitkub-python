"""Tests for models module."""

from bitkub.models import (
    ServerTimeResponse,
    StatusResponse,
    SymbolData,
    SymbolsResponse,
    TickerData,
    TickerResponse,
)


class TestServerTimeResponse:
    """Test ServerTimeResponse model."""

    def test_from_dict_valid(self):
        """Test creating ServerTimeResponse from valid dict."""
        data = {"error": 0, "result": 1633424427}
        response = ServerTimeResponse.from_dict(data)
        assert response.error == 0
        assert response.result == 1633424427

    def test_from_dict_missing_fields(self):
        """Test creating ServerTimeResponse with missing fields."""
        data = {}
        response = ServerTimeResponse.from_dict(data)
        assert response.error == 0  # default
        assert response.result == 0  # default

    def test_from_dict_with_error(self):
        """Test creating ServerTimeResponse with error."""
        data = {"error": 1, "result": 0}
        response = ServerTimeResponse.from_dict(data)
        assert response.error == 1
        assert response.result == 0


class TestStatusResponse:
    """Test StatusResponse model."""

    def test_from_dict_valid(self):
        """Test creating StatusResponse from valid dict."""
        data = {
            "error": 0,
            "result": [
                {"name": "Non-secure endpoints", "status": "ok", "message": ""},
                {"name": "Secure endpoints", "status": "ok", "message": ""},
            ],
        }
        response = StatusResponse.from_dict(data)
        assert response.error == 0
        assert len(response.result) == 2
        assert response.result[0]["name"] == "Non-secure endpoints"

    def test_from_dict_empty_result(self):
        """Test creating StatusResponse with empty result."""
        data = {"error": 0, "result": []}
        response = StatusResponse.from_dict(data)
        assert response.error == 0
        assert response.result == []

    def test_from_dict_missing_result(self):
        """Test creating StatusResponse with missing result."""
        data = {"error": 0}
        response = StatusResponse.from_dict(data)
        assert response.error == 0
        assert response.result == []  # default


class TestSymbolData:
    """Test SymbolData model."""

    def test_from_dict_valid(self):
        """Test creating SymbolData from valid dict."""
        data = {"id": 1, "symbol": "THB_BTC", "info": "Thai Baht to Bitcoin"}
        symbol = SymbolData.from_dict(data)
        assert symbol.id == 1
        assert symbol.symbol == "THB_BTC"
        assert symbol.info == "Thai Baht to Bitcoin"

    def test_from_dict_missing_fields(self):
        """Test creating SymbolData with missing fields."""
        data = {}
        symbol = SymbolData.from_dict(data)
        assert symbol.id == 0  # default
        assert symbol.symbol == ""  # default
        assert symbol.info == ""  # default


class TestSymbolsResponse:
    """Test SymbolsResponse model."""

    def test_from_dict_valid(self):
        """Test creating SymbolsResponse from valid dict."""
        data = {
            "error": 0,
            "result": [
                {"id": 1, "symbol": "THB_BTC", "info": "Thai Baht to Bitcoin"},
                {"id": 2, "symbol": "THB_ETH", "info": "Thai Baht to Ethereum"},
            ],
        }
        response = SymbolsResponse.from_dict(data)
        assert response.error == 0
        assert len(response.result) == 2
        assert response.result[0].symbol == "THB_BTC"
        assert response.result[1].symbol == "THB_ETH"

    def test_from_dict_empty_result(self):
        """Test creating SymbolsResponse with empty result."""
        data = {"error": 0, "result": []}
        response = SymbolsResponse.from_dict(data)
        assert response.error == 0
        assert response.result == []

    def test_from_dict_missing_result(self):
        """Test creating SymbolsResponse with missing result."""
        data = {"error": 0}
        response = SymbolsResponse.from_dict(data)
        assert response.error == 0
        assert response.result == []


class TestTickerData:
    """Test TickerData model."""

    def test_from_dict_valid(self):
        """Test creating TickerData from valid dict."""
        data = {
            "id": 1,
            "last": 2418999.8,
            "lowestAsk": 2418999.8,
            "highestBid": 2416599.78,
            "percentChange": 1.5,
            "baseVolume": 215.23564897,
            "quoteVolume": 518727096.21,
            "isFrozen": 0,
            "high24hr": 2459000,
            "low24hr": 2370000.01,
            "change": 23999.81,
        }
        ticker = TickerData.from_dict(data)
        assert ticker.id == 1
        assert ticker.last == 2418999.8
        assert ticker.percentChange == 1.5
        assert ticker.isFrozen is False  # 0 -> False

    def test_from_dict_missing_fields(self):
        """Test creating TickerData with missing fields."""
        data = {}
        ticker = TickerData.from_dict(data)
        assert ticker.id == 0
        assert ticker.last == 0.0
        assert ticker.isFrozen is False

    def test_from_dict_type_conversion(self):
        """Test TickerData type conversion."""
        data = {
            "id": "1",  # string - not converted to int in current implementation
            "last": "2418999.8",  # string that should convert to float
            "isFrozen": "0",  # string - bool("0") is True in Python
        }
        ticker = TickerData.from_dict(data)
        assert ticker.id == "1"  # Current implementation doesn't convert id to int
        assert ticker.last == 2418999.8
        assert ticker.isFrozen is True  # bool("0") is True in Python


class TestTickerResponse:
    """Test TickerResponse model."""

    def test_from_dict_valid(self):
        """Test creating TickerResponse from valid dict."""
        data = {
            "error": 0,
            "result": {
                "THB_BTC": {
                    "id": 1,
                    "last": 2418999.8,
                    "lowestAsk": 2418999.8,
                    "highestBid": 2416599.78,
                    "percentChange": 1.5,
                    "baseVolume": 215.23564897,
                    "quoteVolume": 518727096.21,
                    "isFrozen": 0,
                    "high24hr": 2459000,
                    "low24hr": 2370000.01,
                    "change": 23999.81,
                }
            },
        }
        response = TickerResponse.from_dict(data)
        assert response.error == 0
        assert "THB_BTC" in response.result
        assert response.result["THB_BTC"].last == 2418999.8

    def test_from_dict_multiple_tickers(self):
        """Test creating TickerResponse with multiple tickers."""
        data = {
            "error": 0,
            "result": {
                "THB_BTC": {"id": 1, "last": 2418999.8},
                "THB_ETH": {"id": 2, "last": 138931.8},
            },
        }
        response = TickerResponse.from_dict(data)
        assert response.error == 0
        assert len(response.result) == 2
        assert "THB_BTC" in response.result
        assert "THB_ETH" in response.result

    def test_from_dict_empty_result(self):
        """Test creating TickerResponse with empty result."""
        data = {"error": 0, "result": {}}
        response = TickerResponse.from_dict(data)
        assert response.error == 0
        assert response.result == {}

    def test_from_dict_missing_result(self):
        """Test creating TickerResponse with missing result."""
        data = {"error": 0}
        response = TickerResponse.from_dict(data)
        assert response.error == 0
        assert response.result == {}


# Test edge cases and error handling
class TestModelsEdgeCases:
    """Test edge cases and error handling in models."""

    def test_models_handle_malformed_data_gracefully(self):
        """Test models can handle some malformed data gracefully."""
        # Test with missing required fields but valid dict structure
        malformed_data = {"unexpected_field": "value"}

        # Should not raise exceptions, just use defaults
        server_time = ServerTimeResponse.from_dict(malformed_data)
        status = StatusResponse.from_dict(malformed_data)
        symbols = SymbolsResponse.from_dict(malformed_data)
        ticker = TickerResponse.from_dict(malformed_data)

        assert server_time.error == 0  # default
        assert status.error == 0  # default
        assert symbols.error == 0  # default
        assert ticker.error == 0  # default

    def test_symbol_data_with_partial_data(self):
        """Test SymbolData with partial data."""
        data = {"id": 5, "symbol": "THB_DOGE"}  # missing info
        symbol = SymbolData.from_dict(data)

        assert symbol.id == 5
        assert symbol.symbol == "THB_DOGE"
        assert symbol.info == ""  # default

    def test_ticker_data_with_string_numbers(self):
        """Test TickerData handles string numbers correctly."""
        data = {
            "id": "42",  # Not converted to int
            "last": "1234.56",
            "lowestAsk": "1235.00",
            "percentChange": "-2.5",
        }
        ticker = TickerData.from_dict(data)

        assert ticker.id == "42"  # Current implementation doesn't convert id
        assert ticker.last == 1234.56
        assert ticker.lowestAsk == 1235.00
        assert ticker.percentChange == -2.5

    def test_boolean_conversion_edge_cases(self):
        """Test boolean conversion in TickerData."""
        # Test various truthy/falsy values - Python's bool() behavior
        test_cases = [
            (0, False),
            (1, True),
            ("0", True),  # bool("0") is True in Python
            ("1", True),
            ("", False),  # Empty string is False
            (False, False),
            (True, True),
        ]

        for input_val, expected in test_cases:
            data = {"isFrozen": input_val}
            ticker = TickerData.from_dict(data)
            assert ticker.isFrozen == expected, f"Failed for input {input_val}"

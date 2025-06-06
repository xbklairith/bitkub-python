"""Response models for Bitkub API."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union


@dataclass
class APIResponse:
    """Base class for all API responses."""

    error: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIResponse":
        """Create instance from API response dictionary."""
        return cls(error=data.get("error", 0))


@dataclass
class ServerTimeResponse(APIResponse):
    """Response for server time endpoint."""

    result: int  # Unix timestamp

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ServerTimeResponse":
        return cls(error=data.get("error", 0), result=data.get("result", 0))


@dataclass
class StatusResponse(APIResponse):
    """Response for status endpoint."""

    result: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatusResponse":
        return cls(error=data.get("error", 0), result=data.get("result", []))


@dataclass
class SymbolData:
    """Symbol information."""

    id: int
    symbol: str
    info: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolData":
        return cls(
            id=data.get("id", 0),
            symbol=data.get("symbol", ""),
            info=data.get("info", ""),
        )


@dataclass
class SymbolsResponse(APIResponse):
    """Response for symbols endpoint."""

    result: List[SymbolData]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SymbolsResponse":
        result_data = data.get("result", [])
        symbols = [SymbolData.from_dict(item) for item in result_data]
        return cls(error=data.get("error", 0), result=symbols)


@dataclass
class TickerData:
    """Ticker information for a trading pair."""

    id: int
    last: float
    lowestAsk: float
    highestBid: float
    percentChange: float
    baseVolume: float
    quoteVolume: float
    isFrozen: bool
    high24hr: float
    low24hr: float
    change: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TickerData":
        return cls(
            id=data.get("id", 0),
            last=float(data.get("last", 0)),
            lowestAsk=float(data.get("lowestAsk", 0)),
            highestBid=float(data.get("highestBid", 0)),
            percentChange=float(data.get("percentChange", 0)),
            baseVolume=float(data.get("baseVolume", 0)),
            quoteVolume=float(data.get("quoteVolume", 0)),
            isFrozen=bool(data.get("isFrozen", False)),
            high24hr=float(data.get("high24hr", 0)),
            low24hr=float(data.get("low24hr", 0)),
            change=float(data.get("change", 0)),
        )


@dataclass
class TickerResponse(APIResponse):
    """Response for ticker endpoint."""

    result: Dict[str, TickerData]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TickerResponse":
        result_data = data.get("result", {})
        tickers = {
            symbol: TickerData.from_dict(ticker_data)
            for symbol, ticker_data in result_data.items()
        }
        return cls(error=data.get("error", 0), result=tickers)


@dataclass
class TradeData:
    """Individual trade information."""

    txn_id: str
    rate: float
    amount: float
    ts: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeData":
        return cls(
            txn_id=str(data.get("txn_id", "")),
            rate=float(data.get("rate", 0)),
            amount=float(data.get("amount", 0)),
            ts=int(data.get("ts", 0)),
        )


@dataclass
class TradesResponse(APIResponse):
    """Response for trades endpoint."""

    result: List[TradeData]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradesResponse":
        result_data = data.get("result", [])
        trades = [TradeData.from_dict(trade) for trade in result_data]
        return cls(error=data.get("error", 0), result=trades)


@dataclass
class OrderBookEntry:
    """Order book entry (bid or ask)."""

    id: int
    rate: float
    amount: float

    @classmethod
    def from_dict(cls, data: List[Union[str, int, float]]) -> "OrderBookEntry":
        """Create from array format [id, rate, amount]."""
        return cls(
            id=int(data[0]) if len(data) > 0 else 0,
            rate=float(data[1]) if len(data) > 1 else 0.0,
            amount=float(data[2]) if len(data) > 2 else 0.0,
        )


@dataclass
class OrderBookResponse(APIResponse):
    """Response for order book endpoint."""

    result: List[OrderBookEntry]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderBookResponse":
        result_data = data.get("result", [])
        orders = [OrderBookEntry.from_dict(entry) for entry in result_data]
        return cls(error=data.get("error", 0), result=orders)


@dataclass
class DepthData:
    """Market depth data."""

    bids: List[List[float]]
    asks: List[List[float]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DepthData":
        return cls(bids=data.get("bids", []), asks=data.get("asks", []))


@dataclass
class DepthResponse(APIResponse):
    """Response for depth endpoint."""

    result: DepthData

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DepthResponse":
        result_data = data.get("result", {})
        return cls(error=data.get("error", 0), result=DepthData.from_dict(result_data))


@dataclass
class WalletBalance:
    """Wallet balance for a currency."""

    available: float
    reserved: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WalletBalance":
        return cls(
            available=float(data.get("available", 0)),
            reserved=float(data.get("reserved", 0)),
        )


@dataclass
class WalletResponse(APIResponse):
    """Response for wallet endpoint."""

    result: Dict[str, float]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WalletResponse":
        return cls(error=data.get("error", 0), result=data.get("result", {}))


@dataclass
class BalancesResponse(APIResponse):
    """Response for balances endpoint."""

    result: Dict[str, WalletBalance]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BalancesResponse":
        result_data = data.get("result", {})
        balances = {
            currency: WalletBalance.from_dict(balance_data)
            for currency, balance_data in result_data.items()
        }
        return cls(error=data.get("error", 0), result=balances)


@dataclass
class OrderResult:
    """Order creation result."""

    id: str
    hash: str
    typ: str
    amt: float
    rat: float
    fee: float
    cre: float
    rec: float
    ts: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderResult":
        return cls(
            id=str(data.get("id", "")),
            hash=str(data.get("hash", "")),
            typ=str(data.get("typ", "")),
            amt=float(data.get("amt", 0)),
            rat=float(data.get("rat", 0)),
            fee=float(data.get("fee", 0)),
            cre=float(data.get("cre", 0)),
            rec=float(data.get("rec", 0)),
            ts=int(data.get("ts", 0)),
        )


@dataclass
class OrderResponse(APIResponse):
    """Response for order creation."""

    result: Optional[OrderResult]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderResponse":
        result_data = data.get("result")
        result = OrderResult.from_dict(result_data) if result_data else None
        return cls(error=data.get("error", 0), result=result)


@dataclass
class UserLimitsData:
    """User trading limits."""

    usage: Dict[str, Any]
    rate: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserLimitsData":
        return cls(usage=data.get("usage", {}), rate=data.get("rate", {}))


@dataclass
class UserLimitsResponse(APIResponse):
    """Response for user limits endpoint."""

    result: UserLimitsData

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserLimitsResponse":
        result_data = data.get("result", {})
        return cls(
            error=data.get("error", 0), result=UserLimitsData.from_dict(result_data)
        )


@dataclass
class TradingCreditsResponse(APIResponse):
    """Response for trading credits endpoint."""

    result: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradingCreditsResponse":
        return cls(error=data.get("error", 0), result=int(data.get("result", 0)))

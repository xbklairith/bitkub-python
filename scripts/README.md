# Bitkub API Validation Scripts

Essential scripts to validate the Bitkub Python client against the real API.

## Scripts

### 🧪 `validate_comprehensive.py` - Main Validation
**Purpose**: Comprehensive API testing with real market data  
**Use**: Primary validation script for the client

```bash
python scripts/validate_comprehensive.py
```

**Features**:
- Tests all 11 public API endpoints
- Shows real market data (BTC price, trading pairs)
- API structure analysis
- Real-time market data sample
- Order book and depth analysis
- TradingView chart data

### ⚡ `validate_quick.py` - Quick Validation  
**Purpose**: Fast basic functionality test  
**Use**: Quick smoke test, ideal for CI/CD

```bash
python scripts/validate_quick.py
```

**Features**:
- Core endpoint validation (7 key APIs)
- Shows current BTC price
- Top trading pairs by volume
- Market depth and recent trades
- Completes in ~1-2 seconds

### 🌐 `validate_network.py` - Network Diagnostics
**Purpose**: Network connectivity and performance testing  
**Use**: Diagnose connection issues or performance problems

```bash
python scripts/validate_network.py
```

**Features**:
- Network connectivity testing
- Response time analysis for all endpoints
- Rate limiting validation
- Data consistency checks
- Error handling verification

## Usage

All scripts work without API keys (public endpoints only):

```bash
# Quick validation
python scripts/validate_quick.py

# Comprehensive testing  
python scripts/validate_comprehensive.py

# Network diagnostics
python scripts/validate_network.py
```

## Expected Results

- ✅ **BTC Price**: ~3,330,000 THB (live market data)
- ✅ **Response Times**: 0.08-0.5 seconds
- ✅ **188 Trading Symbols** available
- ✅ **100% Endpoint Success** rate

All scripts handle the actual Bitkub API format correctly.
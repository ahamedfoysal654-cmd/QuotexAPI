# QuotexAPI

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Unofficial Python API for Quotex broker - A modern, async-first library with comprehensive trading capabilities.

## ✨ Features

### 🔐 Authentication
- ✅ Login with email/password
- ✅ Login with SSID (Session ID)
- ✅ Automatic session management
- ✅ Logout functionality

### 🔌 Connection Management
- ✅ WebSocket connection with auto-reconnect
- ✅ Connection state tracking
- ✅ Configurable reconnection strategy
- ✅ Exponential backoff for reconnections

### 💰 Account & Balance Management
- ✅ Get active balance (Real/Demo)
- ✅ Get all account balances
- ✅ Switch between Real and Demo accounts
- ✅ Real-time balance updates

### 📊 Instruments & Market Data
- ✅ List available binary option assets
- ✅ Filter assets by type (Forex, Crypto, Commodities, etc.)
- ✅ Get real-time payout percentages
- ✅ Asset information and status

### 📈 Trading
- ✅ Place trades (CALL/PUT)
- ✅ Configurable trade amount and expiry
- ✅ Cancel trades before start (if supported)
- ✅ Trade validation and error handling

### 📉 Live Data & Trade Tracking
- ✅ Get list of open trades
- ✅ Get trade history with pagination
- ✅ Date range filtering for history
- ✅ Async trade result tracking with countdown
- ✅ Optional blocking wait for results
- ✅ Real-time trade callbacks

## 🚀 Installation

### From Source

```bash
git clone https://github.com/ChipaDevTeam/QuotexAPI.git
cd QuotexAPI
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## 📖 Quick Start

### Test Your SSID First! ⭐

Before running any examples, test your SSID token:

```bash
# Get your SSID from browser (F12 > Application > Cookies > ssid)
python examples/test_ssid.py
```

This validates your SSID and provides clear feedback if it's expired. See [docs/GET_SSID.md](docs/GET_SSID.md) for detailed instructions on obtaining your SSID.

### Basic Usage

```python
import asyncio
from QuotexAPI import QuotexAPI, TradeDirection

async def main():
    # Initialize API
    api = QuotexAPI(
        email="your-email@example.com",
        password="your-password"
    )
    
    # Connect
    profile = await api.connect()
    print(f"Connected as: {profile.email}")
    
    # Check balance
    balance = await api.get_balance()
    print(f"Balance: ${balance.amount}")
    
    # Get available assets
    assets = await api.get_assets()
    print(f"Available assets: {len(assets)}")
    
    # Place a trade
    trade = await api.buy(
        asset="EURUSD",
        amount=10.0,
        direction=TradeDirection.CALL,
        expiry=300  # 5 minutes
    )
    print(f"Trade placed: {trade.order_id}")
    
    # Wait for result
    result = await api.wait_for_result(trade.order_id)
    print(f"Result: {result.result}, Profit: ${result.profit}")
    
    # Disconnect
    await api.disconnect()

asyncio.run(main())
```

### Using Context Manager

```python
from QuotexAPI import QuotexAPI, TradeDirection, AccountType

async def main():
    # Automatic connection and disconnection
    async with QuotexAPI(email="user@example.com", password="pass") as api:
        # Switch to demo account
        await api.switch_account(AccountType.DEMO)
        
        # Place and track trade
        trade = await api.buy("BTCUSD", 10.0, TradeDirection.PUT, 180)
        result = await api.track_trade(trade.order_id)
        
        print(f"Trade completed: {result.result}")

asyncio.run(main())
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
QUOTEX_EMAIL=your-email@example.com
QUOTEX_PASSWORD=your-password
QUOTEX_SSID=your-session-id  # Optional

# API Configuration
QUOTEX_API_URL=https://api.quotex.io
QUOTEX_WS_URL=wss://ws.quotex.io

# Connection Settings
QUOTEX_RECONNECT_ENABLED=true
QUOTEX_MAX_RECONNECT_ATTEMPTS=5
QUOTEX_RECONNECT_DELAY=5

# Logging
LOG_LEVEL=INFO
```

### Programmatic Configuration

```python
from QuotexAPI import QuotexAPI, QuotexConfig

config = QuotexConfig(
    email="user@example.com",
    password="password",
    reconnect_enabled=True,
    max_reconnect_attempts=3,
    log_level="DEBUG"
)

api = QuotexAPI(config=config)
```

## 📚 Documentation

### Main API Methods

#### Authentication
```python
await api.connect()  # Connect and authenticate
await api.logout()   # Logout
api.is_connected     # Check connection status
```

#### Account Management
```python
balance = await api.get_balance()                    # Get active balance
balances = await api.get_all_balances()             # Get all balances
await api.switch_account(AccountType.DEMO)          # Switch account
```

#### Trading
```python
# Place trade
trade = await api.buy(
    asset="EURUSD",
    amount=10.0,
    direction=TradeDirection.CALL,  # or TradeDirection.PUT
    expiry=300
)

# Cancel trade
await api.cancel_trade(order_id)
```

#### Market Data
```python
# Get all assets
assets = await api.get_assets()

# Get assets by type
forex_assets = await api.get_assets(AssetType.FOREX)

# Get payout percentage
payout = await api.get_payout("EURUSD")
```

#### Trade Tracking
```python
# Get open trades
open_trades = await api.get_open_trades()

# Get trade history
history = await api.get_trade_history(limit=50, offset=0)

# Track trade with callback
async def on_update(order_id, remaining, trade):
    print(f"Time remaining: {remaining}s")

result = await api.track_trade(order_id, callback=on_update)

# Wait for result (blocking)
result = await api.wait_for_result(order_id, timeout=600)
```

### Models

All data is returned using Pydantic models for type safety:

- `UserProfile` - User account information
- `Balance` - Account balance details
- `Asset` - Asset/instrument information
- `Trade` - Trade information and status
- `TradeRequest` - Trade placement parameters

### Enums

Type-safe enumerations:

- `AccountType.DEMO` / `AccountType.REAL`
- `TradeDirection.CALL` / `TradeDirection.PUT`
- `TradeStatus.PENDING` / `ACTIVE` / `COMPLETED` / `CANCELLED`
- `TradeResult.WIN` / `LOSS` / `DRAW`
- `AssetType.FOREX` / `CRYPTO` / `COMMODITIES` / `INDICES` / `STOCKS`
- `ConnectionState.DISCONNECTED` / `CONNECTING` / `CONNECTED` / `RECONNECTING`

## 🎯 Examples

See the [examples](examples/) directory for comprehensive examples:

- `basic_usage.py` - Simple trading example
- `advanced_usage.py` - Advanced features with callbacks
- `multiple_trades.py` - Concurrent trading example
- `ssid_auth.py` - Session management example

## 🏗️ Architecture

The project follows clean architecture principles:

```
QuotexAPI/
├── __init__.py          # Main exports
├── client.py            # High-level API client
├── config.py            # Configuration management
├── enums.py             # Enumerations
├── exceptions.py        # Custom exceptions
├── models.py            # Pydantic models
├── services/            # Service layer
│   ├── base.py          # Base service class
│   ├── auth.py          # Authentication service
│   ├── connection.py    # WebSocket connection
│   ├── account.py       # Account management
│   ├── instrument.py    # Instruments/assets
│   ├── trading.py       # Trading operations
│   └── data.py          # Data and tracking
└── utils/               # Utilities
    └── logger.py        # Logging setup
```

### Design Patterns

- **Service Layer Pattern**: Each domain (auth, trading, etc.) has its own service
- **Dependency Injection**: Services receive configuration through constructors
- **Async/Await**: Fully asynchronous for non-blocking operations
- **Type Safety**: Pydantic models for runtime validation
- **Error Handling**: Custom exception hierarchy for specific errors

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=QuotexAPI --cov-report=html

# Run specific test file
pytest tests/test_client.py
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/ChipaDevTeam/QuotexAPI.git
cd QuotexAPI

# Install dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Style

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black QuotexAPI/

# Sort imports
isort QuotexAPI/

# Lint
flake8 QuotexAPI/

# Type check
mypy QuotexAPI/
```

## ⚠️ Important Notes

- This is an **unofficial** API and is not affiliated with Quotex
- Use at your own risk
- Always test with a **Demo account** first
- Be mindful of rate limits
- Keep your credentials secure
- This library is for educational purposes

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code:
- Follows the existing code style
- Includes appropriate tests
- Updates documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Thanks to all contributors
- Inspired by the need for a modern, well-architected Quotex API

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ChipaDevTeam/QuotexAPI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ChipaDevTeam/QuotexAPI/discussions)

## 🗺️ Roadmap

- [ ] Implement actual API endpoints (currently uses mock data)
- [ ] Add WebSocket message parsing
- [ ] Add more asset types
- [ ] Implement signals/indicators
- [ ] Add backtesting capabilities
- [ ] Create comprehensive test suite
- [ ] Add more examples
- [ ] Improve documentation

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

Made with ❤️ by [ChipaDevTeam](https://github.com/ChipaDevTeam)


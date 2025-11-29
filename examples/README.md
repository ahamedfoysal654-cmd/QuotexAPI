# QuotexAPI Examples

This directory contains example scripts demonstrating how to use the QuotexAPI.

## Prerequisites

Before running the examples, make sure you have:

1. Installed the package and dependencies:
   ```bash
   pip install -e .
   ```

2. Set up your credentials in `.env` file (copy from `.env.example`):
   ```bash
   cp .env.example .env
   # Edit .env and add your credentials
   ```

## Examples

### Test Your SSID First! (Recommended)

#### 0. Test SSID (`test_ssid.py`) ⭐ **START HERE**

Before running other examples, validate your SSID token:
- Tests WebSocket connection
- Verifies SSID authentication
- Provides clear error messages if SSID is expired
- Shows step-by-step connection status

```bash
python examples/test_ssid.py
```

This will help you ensure your SSID is valid before trying the other examples!

### Quick Start Examples (Recommended)

#### 1. Get Balance (`get_balance.py`)

Simple example to check your account balances:
- Connect to Quotex
- Authenticate with SSID
- Retrieve demo and real account balances
- Monitor balance updates

```bash
export QUOTEX_SSID='your_ssid_token'
python examples/get_balance.py
```

#### 2. Get Candles (`get_candles.py`)

Subscribe to real-time candle/depth data:
- Connect and authenticate
- Subscribe to multiple assets
- Receive real-time OHLC candle updates
- Handle incoming market data

```bash
export QUOTEX_SSID='your_ssid_token'
python examples/get_candles.py
```

#### 3. Place Order (`place_order.py`)

Place a binary options trade:
- Check account balance
- Configure trade parameters (asset, direction, amount, expiry)
- Place trade with confirmation
- Wait for trade result
- Check profit/loss

```bash
export QUOTEX_SSID='your_ssid_token'
python examples/place_order.py
```

### Additional Examples

#### 4. Basic Usage (`basic_usage.py`)

The simplest example demonstrating fundamental operations:
- Connecting to the API
- Checking account balance
- Listing available assets
- Placing a trade
- Waiting for trade result

```bash
python examples/basic_usage.py
```

#### 5. Advanced Usage (`advanced_usage.py`)

More advanced features including:
- Using context manager for automatic connection management
- Real-time trade tracking with callbacks
- Getting trade history
- Switching between Demo/Real accounts

```bash
python examples/advanced_usage.py
```

#### 6. Multiple Concurrent Trades (`multiple_trades.py`)

Demonstrates concurrent trading:
- Placing multiple trades simultaneously
- Tracking multiple trades at once
- Calculating win/loss statistics

```bash
python examples/multiple_trades.py
```

#### 7. SSID Authentication (`ssid_auth.py`)

Session management examples:
- Logging in with SSID (Session ID)
- Saving and reusing sessions
- Avoiding repeated email/password authentication

```bash
python examples/ssid_auth.py
```

#### 8. WebSocket Usage (`websocket_usage.py`)

Low-level WebSocket examples:
- Direct WebSocket connection
- Socket.IO protocol usage
- Custom message handling

```bash
python examples/websocket_usage.py
```

## Important Notes

- **Always start with Demo account** when testing
- The examples contain placeholder credentials - replace them with your actual credentials
- Some features may require additional API endpoints to be implemented
- Handle errors appropriately in production code
- Be mindful of rate limits

## Customization

Feel free to modify these examples for your needs. The API is designed to be flexible and easy to use.

For more information, see the main [README.md](../README.md) in the project root.

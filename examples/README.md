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

### 1. Basic Usage (`basic_usage.py`)

The simplest example demonstrating fundamental operations:
- Connecting to the API
- Checking account balance
- Listing available assets
- Placing a trade
- Waiting for trade result

```bash
python examples/basic_usage.py
```

### 2. Advanced Usage (`advanced_usage.py`)

More advanced features including:
- Using context manager for automatic connection management
- Real-time trade tracking with callbacks
- Getting trade history
- Switching between Demo/Real accounts

```bash
python examples/advanced_usage.py
```

### 3. Multiple Concurrent Trades (`multiple_trades.py`)

Demonstrates concurrent trading:
- Placing multiple trades simultaneously
- Tracking multiple trades at once
- Calculating win/loss statistics

```bash
python examples/multiple_trades.py
```

### 4. SSID Authentication (`ssid_auth.py`)

Session management examples:
- Logging in with SSID (Session ID)
- Saving and reusing sessions
- Avoiding repeated email/password authentication

```bash
python examples/ssid_auth.py
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

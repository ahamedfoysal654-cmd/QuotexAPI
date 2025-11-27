# Quick Start Guide

Get started with QuotexAPI in 5 minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/ChipaDevTeam/QuotexAPI.git
cd QuotexAPI

# Install the package
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
QUOTEX_EMAIL=your-email@example.com
QUOTEX_PASSWORD=your-password
LOG_LEVEL=INFO
```

## Your First Trade

Create a file `my_first_trade.py`:

```python
import asyncio
from QuotexAPI import QuotexAPI, TradeDirection

async def main():
    # Initialize and connect
    async with QuotexAPI() as api:  # Reads from .env
        # Check balance
        balance = await api.get_balance()
        print(f"Balance: ${balance.amount}")
        
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
        print(f"Result: {result.result}")
        print(f"Profit: ${result.profit}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python my_first_trade.py
```

## Common Operations

### Check Available Assets

```python
assets = await api.get_assets()
for asset in assets:
    print(f"{asset.name}: {asset.current_payout}%")
```

### Switch to Demo Account

```python
from QuotexAPI import AccountType

await api.switch_account(AccountType.DEMO)
balance = await api.get_balance()
print(f"Demo balance: ${balance.amount}")
```

### Track Trade with Updates

```python
async def on_update(order_id, remaining, trade):
    print(f"Time remaining: {remaining}s")

result = await api.track_trade(order_id, callback=on_update)
```

### Get Trade History

```python
history = await api.get_trade_history(limit=10)
for trade in history:
    print(f"{trade.asset}: {trade.result} (${trade.profit})")
```

## Next Steps

1. **Read the full documentation** in [README.md](../README.md)
2. **Explore examples** in the `examples/` directory
3. **Check the architecture** in [docs/ARCHITECTURE.md](ARCHITECTURE.md)
4. **Run examples**:
   ```bash
   python examples/basic_usage.py
   python examples/advanced_usage.py
   ```

## Tips

- **Always test with Demo account first**
- Check `examples/` for more complex scenarios
- Use logging for debugging: `log_level="DEBUG"`
- Read error messages - they're designed to be helpful
- Check connection state: `api.is_connected`

## Troubleshooting

### Import errors?
```bash
pip install -e .
```

### Authentication fails?
- Check credentials in `.env`
- Ensure email/password are correct
- Try SSID authentication instead

### Connection issues?
- Check internet connection
- Verify API URLs in config
- Check logs for detailed errors

## Getting Help

- **Examples**: Check `examples/` directory
- **Documentation**: Read `README.md`
- **Issues**: [GitHub Issues](https://github.com/ChipaDevTeam/QuotexAPI/issues)
- **Architecture**: See `docs/ARCHITECTURE.md`

Happy trading! 🚀

"""
Basic usage example for QuotexAPI.

This example demonstrates:
- Connecting to the API
- Checking account balance
- Listing available assets
- Placing a simple trade
- Waiting for trade result
"""

import asyncio

from QuotexAPI import QuotexAPI, TradeDirection


async def main():
    # Initialize API client
    # You can pass credentials directly or use .env file
    api = QuotexAPI(
        email="your-email@example.com",
        password="your-password",
        log_level="INFO"
    )

    try:
        # Connect and authenticate
        print("Connecting to Quotex API...")
        profile = await api.connect()
        print(f"✓ Connected as: {profile.email}")
        print(f"✓ Active account: {profile.active_account}")

        # Get account balance
        balance = await api.get_balance()
        print(f"\n💰 Balance: {balance.amount} {balance.currency}")

        # Get available assets
        print("\n📊 Fetching available assets...")
        assets = await api.get_assets()
        print(f"✓ Found {len(assets)} assets")

        # Display first 5 assets
        for asset in assets[:5]:
            print(f"  - {asset.name} ({asset.symbol}): {asset.current_payout}% payout")

        # Place a trade (example - adjust parameters as needed)
        print("\n📈 Placing a trade...")
        trade = await api.buy(
            asset="EURUSD",
            amount=10.0,
            direction=TradeDirection.CALL,
            expiry=300  # 5 minutes
        )
        print(f"✓ Trade placed!")
        print(f"  Order ID: {trade.order_id}")
        print(f"  Asset: {trade.asset}")
        print(f"  Direction: {trade.direction.value.upper()}")
        print(f"  Amount: ${trade.amount}")
        print(f"  Expiry: {trade.expiry}s")

        # Wait for trade result
        print(f"\n⏳ Waiting for trade result...")
        result = await api.wait_for_result(trade.order_id, timeout=600)
        print(f"✓ Trade completed!")
        print(f"  Result: {result.result.value.upper()}")
        print(f"  Profit: ${result.profit}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Disconnect
        print("\n🔌 Disconnecting...")
        await api.disconnect()
        print("✓ Disconnected")


if __name__ == "__main__":
    asyncio.run(main())

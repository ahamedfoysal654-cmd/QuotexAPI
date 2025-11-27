"""
Multiple concurrent trades example.

This example demonstrates:
- Placing multiple trades concurrently
- Tracking multiple trades simultaneously
- Error handling for trades
"""

import asyncio

from QuotexAPI import QuotexAPI, TradeDirection, AssetType


async def track_trade_with_logging(api: QuotexAPI, order_id: str, index: int):
    """Track a single trade with logging."""
    try:
        print(f"[Trade {index}] Tracking {order_id}...")
        result = await api.wait_for_result(order_id, timeout=600)
        
        status_emoji = "✅" if result.profit > 0 else "❌"
        print(f"[Trade {index}] {status_emoji} {result.result.value.upper()}: "
              f"${result.profit:.2f}")
        
        return result
    except Exception as e:
        print(f"[Trade {index}] ❌ Error: {e}")
        return None


async def main():
    api = QuotexAPI(
        email="your-email@example.com",
        password="your-password",
        log_level="INFO"
    )

    try:
        # Connect
        print("Connecting to Quotex API...")
        await api.connect()
        print("✓ Connected\n")

        # Get forex assets
        print("Fetching forex assets...")
        assets = await api.get_assets(AssetType.FOREX)
        print(f"✓ Found {len(assets)} forex assets\n")

        # Select first 3 active assets
        active_assets = [a for a in assets if a.is_active][:3]
        
        # Place multiple trades concurrently
        print(f"Placing {len(active_assets)} trades concurrently...")
        trade_tasks = []
        
        for i, asset in enumerate(active_assets):
            direction = TradeDirection.CALL if i % 2 == 0 else TradeDirection.PUT
            trade_task = api.buy(
                asset=asset.symbol,
                amount=5.0,
                direction=direction,
                expiry=300
            )
            trade_tasks.append(trade_task)

        # Wait for all trades to be placed
        trades = await asyncio.gather(*trade_tasks)
        print(f"✓ All {len(trades)} trades placed\n")

        for i, trade in enumerate(trades):
            print(f"  Trade {i+1}: {trade.asset} {trade.direction.value.upper()} "
                  f"(Order: {trade.order_id})")

        print("\nTracking all trades...")
        
        # Track all trades concurrently
        tracking_tasks = [
            track_trade_with_logging(api, trade.order_id, i+1)
            for i, trade in enumerate(trades)
        ]
        
        results = await asyncio.gather(*tracking_tasks, return_exceptions=True)
        
        # Calculate summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        successful = [r for r in results if r and hasattr(r, 'profit')]
        wins = [r for r in successful if r.profit > 0]
        losses = [r for r in successful if r.profit <= 0]
        total_profit = sum(r.profit for r in successful)
        
        print(f"Total trades: {len(trades)}")
        print(f"Wins: {len(wins)}")
        print(f"Losses: {len(losses)}")
        print(f"Total profit: ${total_profit:.2f}")
        print(f"Win rate: {len(wins)/len(successful)*100:.1f}%")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await api.disconnect()
        print("\n✓ Disconnected")


if __name__ == "__main__":
    asyncio.run(main())

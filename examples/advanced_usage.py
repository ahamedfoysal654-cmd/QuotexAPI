"""
Advanced usage example with trade tracking and callbacks.

This example demonstrates:
- Using context manager for automatic connection management
- Real-time trade tracking with callbacks
- Getting trade history
- Switching between accounts
"""

import asyncio

from QuotexAPI import QuotexAPI, AccountType, TradeDirection


async def trade_update_callback(order_id: str, remaining: float, trade):
    """Callback function for trade updates."""
    if remaining > 0:
        print(f"⏱️  Trade {order_id}: {remaining:.0f}s remaining...")
    else:
        print(f"✓ Trade completed: {trade.result.value.upper()} (${trade.profit})")


async def main():
    # Using context manager for automatic connection/disconnection
    async with QuotexAPI(
        email="your-email@example.com",
        password="your-password",
        log_level="INFO"
    ) as api:
        
        print("=" * 60)
        print("QuotexAPI - Advanced Example")
        print("=" * 60)

        # Check all balances
        print("\n1. Checking account balances...")
        balances = await api.get_all_balances()
        for balance in balances:
            status = "✓ ACTIVE" if balance.is_active else ""
            print(f"  {balance.account_type.value.upper()}: "
                  f"${balance.amount} {balance.currency} {status}")

        # Switch to demo account if not already active
        if not any(b.is_active and b.account_type == AccountType.DEMO 
                   for b in balances):
            print("\n2. Switching to Demo account...")
            await api.switch_account(AccountType.DEMO)
            print("  ✓ Switched to Demo account")

        # Get asset information
        print("\n3. Getting asset information...")
        payout = await api.get_payout("EURUSD")
        print(f"  EUR/USD payout: {payout}%")

        # Place a trade
        print("\n4. Placing a trade...")
        trade = await api.buy(
            asset="EURUSD",
            amount=10.0,
            direction=TradeDirection.PUT,
            expiry=180  # 3 minutes
        )
        print(f"  ✓ Trade placed: {trade.order_id}")

        # Track trade with real-time updates
        print("\n5. Tracking trade progress...")
        result = await api.track_trade(trade.order_id, callback=trade_update_callback)

        # Get open trades
        print("\n6. Checking open trades...")
        open_trades = await api.get_open_trades()
        print(f"  Active trades: {len(open_trades)}")
        for t in open_trades:
            print(f"    - {t.asset} {t.direction.value} ${t.amount}")

        # Get trade history
        print("\n7. Fetching trade history...")
        history = await api.get_trade_history(limit=5)
        print(f"  Recent trades: {len(history)}")
        for t in history:
            profit_str = f"+${t.profit}" if t.profit > 0 else f"${t.profit}"
            print(f"    - {t.asset} {t.direction.value}: "
                  f"{t.result.value.upper()} {profit_str}")

        print("\n" + "=" * 60)
        print("Example completed successfully!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

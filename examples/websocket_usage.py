"""
WebSocket Real-time Trading Example
===================================

This example demonstrates the WebSocket-based architecture of QuotexAPI:
- All operations use WebSocket messages (no REST API)
- Real-time data streaming
- Event-driven trade updates
- Automatic message routing
"""

import asyncio
from QuotexAPI import QuotexAPI
from QuotexAPI.enums import TradeDirection


async def websocket_trading_demo():
    """Demonstrate WebSocket-based trading with real-time updates."""
    
    # Initialize API client
    api = QuotexAPI(
        email="your@email.com",
        password="your_password"
    )
    
    print("=" * 60)
    print("WebSocket Trading Demo")
    print("=" * 60)
    
    try:
        # Step 1: Establish WebSocket connection
        print("\n[1] Connecting via WebSocket...")
        await api.connect()
        print("✓ WebSocket connected")
        
        # Step 2: Login via WebSocket message
        print("\n[2] Logging in (via WebSocket message)...")
        profile = await api.login()
        print(f"✓ Logged in: {profile.email}")
        print(f"  Demo Balance: ${profile.demo_balance:.2f}")
        print(f"  Real Balance: ${profile.real_balance:.2f}")
        
        # Step 3: Subscribe to real-time candle data
        print("\n[3] Subscribing to real-time candles (via WebSocket)...")
        asset = "EURUSD"
        await api.subscribe_candles(asset, timeframe=60)
        
        # Counter for candle updates
        candle_count = [0]
        
        def on_candle_update(candle_data):
            """Handle real-time candle updates pushed via WebSocket."""
            candle_count[0] += 1
            print(f"  Candle #{candle_count[0]}: "
                  f"Close={candle_data.get('close', 'N/A')}, "
                  f"Time={candle_data.get('timestamp', 'N/A')}")
        
        api.on_candle(asset, on_candle_update)
        print(f"✓ Subscribed to {asset} candles (updates will be pushed)")
        
        # Wait a bit to receive some candle updates
        print("  Waiting for candle updates...")
        await asyncio.sleep(5)
        
        # Step 4: Place a trade via WebSocket
        print(f"\n[4] Placing trade (via WebSocket message)...")
        trade = await api.place_trade(
            asset=asset,
            direction=TradeDirection.CALL,
            amount=10.0,
            expiry=60  # 60 seconds
        )
        print(f"✓ Trade placed: {trade.order_id}")
        print(f"  Asset: {trade.asset}")
        print(f"  Direction: {trade.direction.value.upper()}")
        print(f"  Amount: ${trade.amount:.2f}")
        print(f"  Expiry: {trade.expiry}s")
        print(f"  Open Price: {trade.open_price}")
        
        # Step 5: Monitor trade via WebSocket events
        print(f"\n[5] Monitoring trade (via WebSocket events)...")
        
        updates_received = [0]
        
        def on_trade_update(update_data):
            """Handle real-time trade updates pushed via WebSocket."""
            updates_received[0] += 1
            status = update_data.get('status', 'unknown')
            countdown = update_data.get('countdown')
            
            if countdown is not None:
                print(f"  Update #{updates_received[0]}: "
                      f"Status={status}, Countdown={countdown}s")
            else:
                result = update_data.get('result', 'pending')
                profit = update_data.get('profit', 0.0)
                print(f"  Update #{updates_received[0]}: "
                      f"Status={status}, Result={result}, Profit=${profit:.2f}")
        
        api.on_trade_update(trade.order_id, on_trade_update)
        print("✓ Subscribed to trade updates")
        print("  (Updates will be pushed automatically via WebSocket)")
        
        # Step 6: Wait for trade result (non-blocking, event-driven)
        print(f"\n[6] Waiting for trade result...")
        print("  (This waits for WebSocket event, no polling!)")
        
        result = await api.wait_for_result(trade.order_id, timeout=120)
        
        print(f"\n✓ Trade completed!")
        print(f"  Result: {result.get('result', 'unknown').upper()}")
        print(f"  Profit: ${result.get('profit', 0.0):.2f}")
        print(f"  Close Price: {result.get('close_price', 'N/A')}")
        
        # Step 7: Get updated balance via WebSocket
        print(f"\n[7] Getting updated balance (via WebSocket)...")
        balance = await api.get_balance()
        print(f"✓ Current Balance:")
        print(f"  Demo: ${balance.demo_balance:.2f}")
        print(f"  Real: ${balance.real_balance:.2f}")
        print(f"  Active: {balance.active_account.upper()}")
        
        # Step 8: Get open trades via WebSocket
        print(f"\n[8] Getting open trades (via WebSocket)...")
        open_trades = await api.get_open_trades()
        print(f"✓ Found {len(open_trades)} open trade(s)")
        for t in open_trades:
            print(f"  - {t.order_id}: {t.asset} {t.direction.value.upper()} ${t.amount}")
        
        # Step 9: Get trade history via WebSocket
        print(f"\n[9] Getting trade history (via WebSocket)...")
        history = await api.get_trade_history(limit=5)
        print(f"✓ Retrieved {len(history)} recent trade(s)")
        for t in history:
            result_str = t.result.value if t.result else "pending"
            profit_str = f"${t.profit:.2f}" if t.profit else "N/A"
            print(f"  - {t.order_id}: {t.asset} → {result_str} ({profit_str})")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Step 10: Disconnect WebSocket
        print(f"\n[10] Disconnecting...")
        await api.disconnect()
        print("✓ WebSocket disconnected")
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)
    print("\nKey Points:")
    print("  • All operations used WebSocket messages (no REST API)")
    print("  • Real-time updates pushed automatically")
    print("  • Single persistent connection for everything")
    print("  • Event-driven architecture (no polling)")
    print("  • Low latency, efficient communication")


async def realtime_data_streaming():
    """Demonstrate real-time data streaming capabilities."""
    
    print("\n" + "=" * 60)
    print("Real-time Data Streaming Demo")
    print("=" * 60)
    
    api = QuotexAPI(email="your@email.com", password="your_password")
    
    try:
        await api.connect()
        await api.login()
        
        print("\nStreaming live data for multiple assets...")
        
        # Subscribe to multiple assets
        assets = ["EURUSD", "GBPUSD", "USDJPY"]
        
        for asset in assets:
            await api.subscribe_candles(asset, timeframe=60)
            await api.subscribe_quotes(asset)
        
        # Handler for candles
        def on_candle(asset):
            def handler(data):
                print(f"[CANDLE] {asset}: "
                      f"O={data.get('open')} "
                      f"H={data.get('high')} "
                      f"L={data.get('low')} "
                      f"C={data.get('close')}")
            return handler
        
        # Handler for quotes
        def on_quote(asset):
            def handler(data):
                print(f"[QUOTE] {asset}: "
                      f"Price={data.get('price')} "
                      f"Time={data.get('timestamp')}")
            return handler
        
        # Register handlers
        for asset in assets:
            api.on_candle(asset, on_candle(asset))
            api.on_quote(asset, on_quote(asset))
        
        print(f"\n✓ Subscribed to {len(assets)} assets")
        print("  Receiving real-time updates via WebSocket...\n")
        
        # Let it stream for a while
        await asyncio.sleep(30)
        
        # Unsubscribe
        print("\nUnsubscribing...")
        for asset in assets:
            await api.unsubscribe_candles(asset, timeframe=60)
        
        print("✓ Unsubscribed")
        
    finally:
        await api.disconnect()
    
    print("\n" + "=" * 60)
    print("Streaming demo completed!")
    print("=" * 60)


async def multiple_trades_websocket():
    """Place multiple trades and monitor all via WebSocket events."""
    
    print("\n" + "=" * 60)
    print("Multiple Trades WebSocket Demo")
    print("=" * 60)
    
    api = QuotexAPI(email="your@email.com", password="your_password")
    
    try:
        await api.connect()
        await api.login()
        
        print("\nPlacing multiple trades...")
        
        # Place multiple trades
        trades = []
        assets = ["EURUSD", "GBPUSD", "USDJPY"]
        
        for asset in assets:
            trade = await api.place_trade(
                asset=asset,
                direction=TradeDirection.CALL if assets.index(asset) % 2 == 0 else TradeDirection.PUT,
                amount=10.0,
                expiry=60
            )
            trades.append(trade)
            print(f"  ✓ Placed: {trade.order_id} ({asset})")
        
        print(f"\n✓ {len(trades)} trades placed")
        print("  Monitoring all via WebSocket events...\n")
        
        # Track completed trades
        completed = []
        
        def make_handler(order_id):
            def handler(data):
                status = data.get('status')
                if status == 'closed':
                    result = data.get('result')
                    profit = data.get('profit', 0.0)
                    print(f"  ✓ {order_id}: {result.upper()} (${profit:.2f})")
                    completed.append(order_id)
                else:
                    countdown = data.get('countdown')
                    if countdown:
                        print(f"  ⏱ {order_id}: {countdown}s remaining")
            return handler
        
        # Subscribe to all trade updates
        for trade in trades:
            api.on_trade_update(trade.order_id, make_handler(trade.order_id))
        
        # Wait for all to complete
        print("Waiting for all trades to complete...\n")
        while len(completed) < len(trades):
            await asyncio.sleep(1)
        
        print(f"\n✓ All {len(trades)} trades completed!")
        
    finally:
        await api.disconnect()
    
    print("\n" + "=" * 60)
    print("Multiple trades demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("QuotexAPI WebSocket Examples")
    print("============================\n")
    print("Choose a demo:")
    print("1. WebSocket Trading Demo (comprehensive)")
    print("2. Real-time Data Streaming")
    print("3. Multiple Trades with WebSocket")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(websocket_trading_demo())
    elif choice == "2":
        asyncio.run(realtime_data_streaming())
    elif choice == "3":
        asyncio.run(multiple_trades_websocket())
    else:
        print("Invalid choice")

"""
Example: Get Real-time Candle Data

This example demonstrates how to:
1. Connect to Quotex
2. Authenticate with SSID
3. Subscribe to real-time candle/depth data
4. Receive and process candle updates
"""

import asyncio
import os
from datetime import datetime
from QuotexAPI import QuotexAPI


# Callback function for candle updates
async def on_candle_update(data):
    """Handle incoming candle data."""
    asset = data.get("asset", "Unknown")
    timestamp = data.get("time", data.get("timestamp", 0))
    
    # Format timestamp
    if timestamp:
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        time_str = "N/A"
    
    # Extract OHLC data
    open_price = data.get("open", data.get("o", 0))
    high = data.get("high", data.get("h", 0))
    low = data.get("low", data.get("l", 0))
    close = data.get("close", data.get("c", 0))
    volume = data.get("volume", data.get("v", 0))
    
    print(f"\n📊 {asset} @ {time_str}")
    print(f"   Open:   {open_price:.5f}")
    print(f"   High:   {high:.5f}")
    print(f"   Low:    {low:.5f}")
    print(f"   Close:  {close:.5f}")
    print(f"   Volume: {volume}")


async def main():
    """Subscribe to candle data example."""
    
    # Get SSID from environment variable
    ssid = os.getenv("QUOTEX_SSID")
    if not ssid:
        print("❌ Error: QUOTEX_SSID environment variable not set")
        print("Set it with: export QUOTEX_SSID='your_ssid_token'")
        return
    
    # Initialize API
    api = QuotexAPI()
    
    try:
        # Connect to Quotex WebSocket
        print("🔌 Connecting to Quotex...")
        await api.connect()
        print("✅ Connected successfully")
        
        # Authenticate with SSID
        print(f"🔐 Authenticating with SSID...")
        await api.login_with_ssid(ssid)
        print("✅ Authenticated successfully")
        
        # Define assets to monitor
        assets = ["EURUSD", "GBPUSD", "BTCUSD"]
        
        print(f"\n📈 Subscribing to candle data for {len(assets)} assets...")
        
        # Subscribe to candles for each asset
        for asset in assets:
            print(f"   - {asset}")
            
            # Register callback for this asset
            api.data_service.on_candle(f"{asset}_otc", on_candle_update)
            
            # Subscribe to candle stream
            await api.subscribe_candles(asset, timeframe=60)
        
        print("\n✅ Subscriptions active")
        print("="*60)
        print("Listening for real-time candle updates...")
        print("Press Ctrl+C to stop")
        print("="*60)
        
        # Keep connection alive to receive updates
        # In a real application, this would run until interrupted
        try:
            await asyncio.sleep(300)  # Run for 5 minutes
        except KeyboardInterrupt:
            print("\n\n⏸️  Interrupted by user")
        
        # Unsubscribe from all assets
        print("\n🔕 Unsubscribing from candle data...")
        for asset in assets:
            await api.data_service.unsubscribe_candles(asset)
            print(f"   - Unsubscribed from {asset}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Disconnect
        print("\n🔌 Disconnecting...")
        await api.disconnect()
        print("✅ Disconnected")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")

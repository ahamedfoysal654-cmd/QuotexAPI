"""
Example: Get Account Balance

This example demonstrates how to:
1. Connect to Quotex
2. Authenticate with SSID
3. Retrieve account balances (demo and real)
"""

import asyncio
import os
from QuotexAPI import QuotexAPI


async def main():
    """Get account balance example."""
    
    # Get SSID from environment variable
    ssid = input("Your ssid: ")
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
        
        # Get account balances
        print("\n💰 Fetching account balances...")
        balances = await api.get_balances()
        
        # Display balances
        print("\n" + "="*50)
        print("ACCOUNT BALANCES")
        print("="*50)
        print(f"Demo Account:  ${balances['demo']:,.2f}")
        print(f"Real Account:  ${balances['real']:,.2f}")
        print("="*50)
        
        # Subscribe to balance updates (optional)
        print("\n📊 Subscribing to balance updates...")
        print("Balance will update automatically after trades")
        
        # Keep connection alive to receive updates
        print("\n⏳ Keeping connection alive for 10 seconds...")
        await asyncio.sleep(10)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
    finally:
        # Disconnect
        print("\n🔌 Disconnecting...")
        await api.disconnect()
        print("✅ Disconnected")


if __name__ == "__main__":
    asyncio.run(main())

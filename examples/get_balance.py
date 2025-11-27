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
    
    # Get SSID from environment variable or user input
    ssid = os.getenv("QUOTEX_SSID")
    if not ssid:
        print("Enter your Quotex SSID token (session ID only, not the full authorization message)")
        print("Example: dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH")
        ssid = input("SSID: ").strip()
    
    # Extract SSID if user pasted the full authorization message
    if ssid.startswith('42["authorization"'):
        import json
        import re
        # Extract the session value from the message
        match = re.search(r'"session":"([^"]+)"', ssid)
        if match:
            ssid = match.group(1)
            print(f"✓ Extracted SSID: {ssid}")
    
    if not ssid:
        print("❌ Error: SSID is required")
        print("Set it with: export QUOTEX_SSID='your_ssid_token'")
        return
    
    # Initialize API
    api = QuotexAPI()
    
    try:
        # Connect to Quotex WebSocket
        print("🔌 Connecting to Quotex WebSocket...")
        await api.connect()
        print("✅ Connected successfully (received handshake)")
        
        # Authenticate with SSID (send authorization message)
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

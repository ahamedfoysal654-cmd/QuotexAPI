"""
Quick SSID Test - Verify your SSID token is valid

This script quickly tests if your SSID token works with Quotex.
Use this before running the full examples to verify authentication.
"""

import asyncio
import os
import re
from QuotexAPI import QuotexAPI


async def main():
    """Quick SSID validation test."""
    
    print("="*60)
    print("QUOTEX SSID VALIDATOR")
    print("="*60)
    print("\nThis script tests if your SSID token is valid and working.")
    print("Get your SSID from browser: F12 > Application > Cookies > ssid\n")
    
    # Get SSID from environment variable or user input
    ssid = os.getenv("QUOTEX_SSID")
    if not ssid:
        print("Paste your SSID (full format or token only):")
        ssid = input("SSID: ").strip()
    
    # Extract SSID if user pasted the full authorization message
    if '"session":"' in ssid or '"session":' in ssid:
        match = re.search(r'"session"\s*:\s*"([^"]+)"', ssid)
        if match:
            extracted = match.group(1)
            print(f"\n✓ Extracted SSID token: {extracted[:30]}...")
            ssid = extracted
    elif ssid.startswith('42['):
        match = re.search(r'["\']([a-zA-Z0-9_-]{30,})["\']', ssid)
        if match:
            extracted = match.group(1)
            print(f"\n✓ Extracted SSID token: {extracted[:30]}...")
            ssid = extracted
    
    if not ssid:
        print("❌ Error: SSID is required")
        return
    
    # Initialize API
    api = QuotexAPI(ssid=ssid)
    
    print("\n" + "="*60)
    print("TESTING CONNECTION")
    print("="*60)
    
    try:
        # Step 1: Connect to WebSocket
        print("\n[1/3] 🔌 Connecting to Quotex WebSocket...")
        await api.connect()
        print("      ✅ Connected! (received handshake)")
        
        # Step 2: Authenticate with SSID
        print("\n[2/3] 🔐 Authenticating with SSID...")
        await api.login_with_ssid(ssid)
        print("      ✅ Authenticated successfully!")
        
        # Step 3: Test API call
        print("\n[3/3] 💰 Testing API - Getting balances...")
        balances = await api.get_balances()
        print(f"      ✅ Demo Balance: ${balances['demo']:,.2f}")
        print(f"      ✅ Real Balance: ${balances['real']:,.2f}")
        
        # Success!
        print("\n" + "="*60)
        print("✅ SUCCESS! Your SSID is valid and working!")
        print("="*60)
        print("\nYou can now run any of the examples:")
        print("  • python examples/get_balance.py")
        print("  • python examples/get_candles.py")
        print("  • python examples/place_order.py")
        print()
        
        await api.disconnect()
        
    except Exception as e:
        print(f"\n      ❌ Failed: {str(e)}")
        print("\n" + "="*60)
        print("❌ AUTHENTICATION FAILED")
        print("="*60)
        print("\nYour SSID token appears to be expired or invalid.")
        print("\nHow to get a fresh SSID:")
        print("  1. Open https://qxbroker.com in your browser")
        print("  2. Log in to your account")
        print("  3. Press F12 to open Developer Tools")
        print("  4. Go to Application tab (Chrome) or Storage tab (Firefox)")
        print("  5. Expand Cookies → Click on https://qxbroker.com")
        print("  6. Find the 'ssid' cookie and copy its Value")
        print("  7. Run this test again with the fresh SSID")
        print("\nNote: SSID tokens typically expire after a few hours.")
        print()
        
        try:
            await api.disconnect()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())

"""
SSID authentication example.

This example demonstrates:
- Logging in with SSID (Session ID)
- Saving and reusing session
"""

import asyncio

from QuotexAPI import QuotexAPI


async def main():
    # Method 1: Direct SSID login
    print("Method 1: Direct SSID Login")
    print("-" * 40)
    
    api = QuotexAPI(
        ssid="your-session-id-here",
        log_level="INFO"
    )

    try:
        profile = await api.connect()
        print(f"✓ Connected with SSID")
        print(f"  User: {profile.email}")
        print(f"  Account: {profile.active_account}")
        
        balance = await api.get_balance()
        print(f"  Balance: ${balance.amount}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await api.disconnect()

    print("\n" + "=" * 60 + "\n")

    # Method 2: Login with credentials and save SSID
    print("Method 2: Login and Save SSID")
    print("-" * 40)
    
    api2 = QuotexAPI(
        email="your-email@example.com",
        password="your-password",
        log_level="INFO"
    )

    try:
        profile = await api2.connect()
        print(f"✓ Connected with email/password")
        
        # Get and save SSID for future use
        ssid = api2.auth.ssid
        print(f"  SSID: {ssid}")
        print(f"\n  💡 Save this SSID to reuse the session later!")
        print(f"  You can store it in .env file as QUOTEX_SSID={ssid}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await api2.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

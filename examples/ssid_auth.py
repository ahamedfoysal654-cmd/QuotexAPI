"""
SSID Authentication Example for Quotex API
==========================================

This example demonstrates:
- Logging in with SSID (Session ID) using Socket.IO protocol
- Quotex message format: 42["authorization",{"session":"<SSID>","isDemo":1,"tournamentId":0}]
- Saving and reusing session
- Switching between demo and real accounts
"""

import asyncio

from QuotexAPI import QuotexAPI


async def main():
    # Method 1: Direct SSID login (Socket.IO format)
    print("Method 1: Direct SSID Login (Socket.IO)")
    print("-" * 40)
    print("Message format: 42[\"authorization\",{\"session\":\"...\",\"isDemo\":1,\"tournamentId\":0}]")
    print()
    
    # Get your SSID from browser cookies after logging into quotex.io
    SSID = "your-session-id-here"  # Example: "dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH"
    
    api = QuotexAPI()

    try:
        # Connect to WebSocket (Socket.IO handshake happens automatically)
        await api.connect()
        print("✓ WebSocket connected (Socket.IO handshake complete)")
        
        # Authenticate with SSID
        # This sends: 42["authorization",{"session":"...","isDemo":1,"tournamentId":0}]
        profile = await api.login_with_ssid(
            ssid=SSID,
            is_demo=True  # True for demo, False for real account
        )
        print(f"✓ Authenticated with SSID")
        print(f"  User ID: {profile.user_id}")
        print(f"  Email: {profile.email}")
        print(f"  Demo Balance: ${profile.demo_balance:.2f}")
        print(f"  Real Balance: ${profile.real_balance:.2f}")
        print(f"  Active Account: {profile.active_account.upper()}")
        
        balance = await api.get_balance()
        print(f"  Current Balance: ${balance.amount:.2f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
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

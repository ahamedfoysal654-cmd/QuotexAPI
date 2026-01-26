"""Test the updated QuotexAPI with curl-based WebSocket transport."""

import asyncio
from QuotexAPI import QuotexAPI

async def main():
    print("=" * 60)
    print("Testing QuotexAPI with Curl WebSocket Transport")
    print("=" * 60)
    
    # Get SSID
    ssid_input = input("\n🔑 Enter your SSID: ").strip()
    
    # Create API instance
    api = QuotexAPI(ssid=ssid_input)
    
    try:
        # Connect
        print("\n🔌 Connecting...")
        await api.connect()
        print("✅ Connected!")
        
        # Get balance
        print("\n💰 Getting balance...")
        balance = await api.get_balance()
        print(f"Balance: {balance}")
        
        # Keep connection alive briefly
        print("\n⏳ Keeping connection alive for 5 seconds...")
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Disconnect
        print("\n🔌 Disconnecting...")
        await api.disconnect()
        print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())

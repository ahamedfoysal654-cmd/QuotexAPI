"""
Test with python-socketio and aiohttp (better Cloudflare bypass)
"""

import asyncio
import socketio
import json

# Create Socket.IO client
sio = socketio.AsyncClient(
    logger=True,
    engineio_logger=False,
    reconnection=True,
    reconnection_attempts=3
)

@sio.event
async def connect():
    """Handle connection."""
    print("✅ Connected to server!")
    print(f"   Session ID: {sio.sid}")

@sio.event
async def disconnect():
    """Handle disconnection."""
    print("🔌 Disconnected from server")

@sio.event
async def connect_error(data):
    """Handle connection error."""
    print(f"❌ Connection error: {data}")

# Catch all events
@sio.event(namespace='/')
async def __default__(event, *args):
    """Catch all events."""
    print(f"\n📥 Event: {event}")
    if args:
        print(f"   Data: {json.dumps(args, indent=2, default=str)[:300]}")

# Specific event handlers based on your screenshot
@sio.on('authorization')
async def on_authorization(data):
    """Handle authorization response."""
    print(f"🔐 Authorization response: {data}")

@sio.on('s_balance/list')
async def on_balance(data):
    """Handle balance data."""
    print(f"💰 Balance: {json.dumps(data, indent=2)[:200]}")

@sio.on('instruments/list')
async def on_instruments(data):
    """Handle instruments data."""
    print(f"📊 Instruments: {json.dumps(data, indent=2)[:200]}")

@sio.on('pending/list')
async def on_pending(data):
    """Handle pending trades."""
    print(f"⏳ Pending: {json.dumps(data, indent=2)[:200]}")

async def main():
    """Main function."""
    print("=" * 60)
    print("Quotex Socket.IO Test (python-socketio)")
    print("=" * 60)
    
    # Get SSID
    ssid_input = input("\n🔑 Enter SSID or full auth message: ").strip()
    
    # Extract auth data
    auth_data = None
    if ssid_input.startswith('42["authorization"'):
        import re
        match = re.search(r'42\["authorization",(\{.+\})\]', ssid_input)
        if match:
            auth_data = json.loads(match.group(1))
            print(f"📝 Using: session={auth_data.get('session', '')[:20]}..., isDemo={auth_data.get('isDemo')}, tournamentId={auth_data.get('tournamentId')}")
    else:
        auth_data = {"session": ssid_input}
        print(f"📝 Using session: {ssid_input[:20]}...")
    
    url = "https://ws2.qxbroker.com"
    
    try:
        print(f"\n🔌 Connecting to {url}/socket.io...")
        
        # Connect with Socket.IO client (it handles Engine.IO protocol automatically)
        await sio.connect(
            url,
            socketio_path='/socket.io',
            transports=['websocket'],
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/126.0.0.0",
                "Origin": "https://qxbroker.com",
            }
        )
        
        # Wait a moment for connection to establish
        await asyncio.sleep(1)
        
        if sio.connected:
            print("\n🚀 Sending authorization...")
            # Emit authorization event
            await sio.emit('authorization', auth_data)
            
            # Wait for auth response
            await asyncio.sleep(2)
            
            # Request data
            print("\n📤 Requesting balance...")
            await sio.emit('s_balance/list', {"_placeholder": True, "num": 0})
            
            await asyncio.sleep(1)
            print("📤 Requesting instruments...")
            await sio.emit('instruments/list', {"_placeholder": True, "num": 0})
            
            await asyncio.sleep(1)
            print("📤 Requesting pending...")
            await sio.emit('pending/list')
            
            # Keep connection alive for a bit
            print("\n⏳ Waiting for responses (10 seconds)...")
            await asyncio.sleep(10)
            
            # Disconnect
            await sio.disconnect()
        else:
            print("❌ Failed to connect")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Done")

if __name__ == "__main__":
    asyncio.run(main())

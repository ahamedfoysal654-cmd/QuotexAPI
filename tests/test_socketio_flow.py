"""
Test Socket.IO Message Flow with Quotex
Based on observed network traffic showing the actual message sequence.
"""

import asyncio
import websockets
import json

async def test_connection():
    """Test WebSocket connection following the observed message pattern."""
    
    # Connection details from the curl command
    uri = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/126.0.0.0",
        "Origin": "https://qxbroker.com",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    print(f"🔌 Connecting to {uri}...")
    print(f"📋 Headers: {headers}")
    
    try:
        async with websockets.connect(uri, additional_headers=headers) as websocket:
            print("✅ Connected!")
        
        # Expected message sequence based on the screenshot:
        # 1. Server sends: 0{"sid":"...","upgrades":[],"pingInterval":25000,"pingTimeout":5000}
        # 2. Server sends: 40 (namespace connection)
        # 3. Client should send: 42["authorization",{"session":"..."}]
        
        message_count = 0
        
        async def receive_messages():
            """Receive and display messages."""
            nonlocal message_count
            async for message in websocket:
                message_count += 1
                print(f"\n📥 Message {message_count}: {type(message).__name__}")
                
                if isinstance(message, str):
                    # Parse Socket.IO message type
                    if message.startswith('0'):
                        print(f"   🔧 HANDSHAKE: {message}")
                        data = json.loads(message[1:])
                        print(f"   Session ID: {data.get('sid')}")
                        print(f"   Ping Interval: {data.get('pingInterval')}ms")
                        print(f"   Ping Timeout: {data.get('pingTimeout')}ms")
                        
                    elif message.startswith('40'):
                        print(f"   ✅ NAMESPACE CONNECTED: {message}")
                        print("   🚀 Ready to send authorization!")
                        
                    elif message.startswith('42'):
                        # Event message with data
                        data = message[2:]
                        try:
                            parsed = json.loads(data)
                            event_name = parsed[0] if parsed else "unknown"
                            event_data = parsed[1] if len(parsed) > 1 else {}
                            print(f"   📨 EVENT: {event_name}")
                            print(f"   Data: {json.dumps(event_data, indent=2)[:200]}...")
                        except:
                            print(f"   📨 EVENT DATA: {data[:200]}...")
                            
                    elif message.startswith('451'):
                        # Acknowledgment message
                        print(f"   ✔️  ACK: {message}")
                        
                    elif message == '2':
                        print(f"   💓 PING from server")
                        await websocket.send('3')
                        print(f"   📤 Sent PONG")
                        
                    elif message == '3':
                        print(f"   💓 PONG from server")
                        
                    else:
                        print(f"   ❓ UNKNOWN: {message}")
                        
                elif isinstance(message, bytes):
                    print(f"   📦 BINARY MESSAGE: {len(message)} bytes")
                    # Binary messages appear in the screenshot
                    print(f"   Preview: {message[:50]}...")
                
                # Stop after receiving a few messages for testing
                if message_count >= 20:
                    print("\n✋ Stopping after 20 messages...")
                    break
        
        # Start receiving messages
        try:
            await asyncio.wait_for(receive_messages(), timeout=30.0)
        except asyncio.TimeoutError:
            print("\n⏱️  Timeout reached")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
        print(f"\n📊 Total messages received: {message_count}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   This might be due to:")
        print(f"   1. Missing authentication cookies in HTTP headers")
        print(f"   2. Server requires pre-authenticated session")
        print(f"   3. Need to connect through browser first to get session")


async def test_with_authorization():
    """Test connection with authorization message."""
    
    ssid_input = input("Enter your SSID token (or press Enter to skip authorization): ").strip()
    
    # Ask for cookies if available
    print("\n❓ Do you have any cookies from the browser? (Check Network tab → WebSocket → Headers → Cookie)")
    print("   If yes, paste the entire Cookie header value (or press Enter to skip)")
    cookies_input = input("Cookies: ").strip()
    
    # Extract full authorization data if user pasted the Socket.IO message
    auth_data = None
    ssid = ssid_input
    
    if ssid_input.startswith('42["authorization"'):
        # Full Socket.IO message provided - extract the data object
        import re
        match = re.search(r'42\["authorization",(\{.+\})\]', ssid_input)
        if match:
            import json
            auth_data = json.loads(match.group(1))
            ssid = auth_data.get('session', '')
            print(f"📝 Extracted full auth data with isDemo={auth_data.get('isDemo')}, tournamentId={auth_data.get('tournamentId')}")
            print(f"📝 Session token: {ssid[:20]}...")
    elif '"session":"' in ssid_input:
        # Just extract session if it's in some JSON format
        import re
        match = re.search(r'"session":"([^"]+)"', ssid_input)
        if match:
            ssid = match.group(1)
            print(f"📝 Extracted SSID: {ssid[:20]}...")
    elif not ssid_input:
        ssid = ""
    
    uri = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/126.0.0.0",
        "Origin": "https://qxbroker.com",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    if cookies_input:
        headers["Cookie"] = cookies_input
        print(f"🍪 Added cookies to headers")
    
    print(f"🔌 Connecting to {uri}...")
    
    async with websockets.connect(uri, additional_headers=headers) as websocket:
        print("✅ Connected!")
        
        async def receive_and_respond():
            async for message in websocket:
                print(f"\n📥 {message}")
                
                # After receiving handshake (0{...}) and namespace connection (40)
                if message.startswith('40') and ssid:
                    # Send authorization as shown in the screenshot
                    # Use full auth data if provided, otherwise just session
                    if auth_data:
                        import json
                        auth_msg = f'42["authorization",{json.dumps(auth_data)}]'
                    else:
                        auth_msg = f'42["authorization",{{"session":"{ssid}"}}]'
                    print(f"\n📤 Sending authorization: {auth_msg[:80]}...")
                    await websocket.send(auth_msg)
                    
                    # After auth, typically you'd request data
                    # Examples from screenshot:
                    # 42["instruments/list",{"_placeholder":true,"num":0}]
                    # 42["s_balance/list",{"_placeholder":true,"num":0}]
                    await asyncio.sleep(0.5)
                    
                    print("\n📤 Requesting instruments list...")
                    await websocket.send('42["instruments/list",{"_placeholder":true,"num":0}]')
                    
                    await asyncio.sleep(0.5)
                    print("\n📤 Requesting balance...")
                    await websocket.send('42["s_balance/list",{"_placeholder":true,"num":0}]')
                    
                elif message == '2':
                    await websocket.send('3')
                    print("💓 PONG")
        
        try:
            await asyncio.wait_for(receive_and_respond(), timeout=30.0)
        except asyncio.TimeoutError:
            print("\n⏱️  Done")


if __name__ == "__main__":
    print("=" * 60)
    print("Quotex Socket.IO Connection Test")
    print("=" * 60)
    print("\nChoose test mode:")
    print("1. Basic connection (no auth)")
    print("2. Connection with authorization")
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "2":
        asyncio.run(test_with_authorization())
    else:
        asyncio.run(test_connection())

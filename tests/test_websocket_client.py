"""
Test with websocket-client library (better browser compatibility)
"""

import websocket
import json
import time

def on_message(ws, message):
    """Handle incoming messages."""
    print(f"\n📥 Received: {message[:200]}")
    
    if isinstance(message, str):
        if message.startswith('0'):
            # Handshake
            data = json.loads(message[1:])
            print(f"   🔧 HANDSHAKE - SID: {data.get('sid')}")
            
        elif message.startswith('40'):
            print(f"   ✅ NAMESPACE CONNECTED")
            
            # Send authorization
            ssid = input("\n🔑 Enter SSID (or Enter to skip): ").strip()
            if ssid:
                if ssid.startswith('42["authorization"'):
                    # Extract the auth data
                    import re
                    match = re.search(r'42\["authorization",(\{.+\})\]', ssid)
                    if match:
                        auth_data = json.loads(match.group(1))
                        auth_msg = f'42["authorization",{json.dumps(auth_data)}]'
                    else:
                        auth_msg = ssid
                else:
                    auth_msg = f'42["authorization",{{"session":"{ssid}"}}]'
                
                print(f"\n📤 Sending auth: {auth_msg[:80]}...")
                ws.send(auth_msg)
                
                # Request data
                time.sleep(0.5)
                print("\n📤 Requesting balance...")
                ws.send('42["s_balance/list",{"_placeholder":true,"num":0}]')
                
                time.sleep(0.5)
                print("📤 Requesting instruments...")
                ws.send('42["instruments/list",{"_placeholder":true,"num":0}]')
                
        elif message.startswith('42'):
            # Event message
            try:
                data = json.loads(message[2:])
                event = data[0] if data else "unknown"
                print(f"   📨 EVENT: {event}")
                if len(data) > 1:
                    print(f"   Data preview: {str(data[1])[:150]}")
            except:
                print(f"   📨 EVENT DATA: {message[2:][:150]}")
                
        elif message.startswith('451'):
            print(f"   ✔️  ACK: {message[:150]}")
            
        elif message == '2':
            print(f"   💓 PING - sending PONG")
            ws.send('3')
            
        elif message == '3':
            print(f"   💓 PONG")

def on_error(ws, error):
    """Handle errors."""
    print(f"\n❌ Error: {error}")

def on_close(ws, close_status_code, close_msg):
    """Handle connection close."""
    print(f"\n🔌 Connection closed: {close_status_code} - {close_msg}")

def on_open(ws):
    """Handle connection open."""
    print("✅ WebSocket Connected!")
    print("Waiting for messages... (Press Ctrl+C to stop)\n")

if __name__ == "__main__":
    # Enable trace for debugging (comment out if too verbose)
    # websocket.enableTrace(True)
    
    uri = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/126.0.0.0",
        "Origin": "https://qxbroker.com",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    print("=" * 60)
    print("Quotex WebSocket Test (websocket-client)")
    print("=" * 60)
    print(f"\n🔌 Connecting to {uri}...\n")
    
    # Create WebSocket connection
    ws = websocket.WebSocketApp(
        uri,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Run forever (blocking)
    ws.run_forever()

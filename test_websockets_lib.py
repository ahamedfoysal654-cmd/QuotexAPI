"""
Test with websockets library using custom SSL and headers.
"""

import asyncio
import json
import ssl
import websockets

async def test_websocket():
    url = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"
    
    # Create custom SSL context that's more permissive
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # Custom headers matching browser
    headers = {
        'Origin': 'https://qxbroker.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/126.0.0.0',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
    }
    
    print("Connecting...")
    try:
        async with websockets.connect(
            url,
            extra_headers=headers,
            ssl=ssl_context,
            ping_interval=None,
            ping_timeout=None
        ) as ws:
            print("Connected!")
            
            # Receive handshake
            msg = await ws.recv()
            print(f"Received: {msg}")
            
            # Receive namespace connect
            msg = await ws.recv()
            print(f"Received: {msg}")
            
            # Send authorization
            ssid = "op86rXkNQhMwqhlhScd45R4xlIbN2CnHRlelpFCw"
            auth_msg = json.dumps(["authorization", {"session": ssid, "isDemo": 1, "tournamentId": 0}])
            await ws.send(f"42{auth_msg}")
            print(f"Sent auth")
            
            # Wait a bit
            await asyncio.sleep(1)
            
            # Send trade
            trade_data = {
                "asset": "EURUSD",
                "amount": 1,
                "time": 60,
                "action": "call",
                "isDemo": 1,
                "tournamentId": 0,
                "requestId": 1769440000000,
                "optionType": 100
            }
            trade_msg = json.dumps(["orders/open", trade_data])
            await ws.send(f"42{trade_msg}")
            print(f"Sent trade: {trade_msg[:100]}...")
            
            # Wait for responses
            print("Waiting for responses...")
            for i in range(10):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    print(f"Received: {msg}")
                except asyncio.TimeoutError:
                    print(".", end="", flush=True)
            
            print("\nDone!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())

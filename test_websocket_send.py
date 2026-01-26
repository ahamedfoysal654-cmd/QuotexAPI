"""
Test WebSocket sending to see raw messages.
"""

import asyncio
import time
from QuotexAPI import QuotexAPI

async def main():
    # Get SSID from user
    ssid_input = input("Enter SSID: ").strip()
    if ssid_input.startswith('42["authorization"'):
        import json
        auth_data = json.loads(ssid_input[2:])
        ssid = auth_data[1]["session"]
    else:
        ssid = ssid_input
    
    print(f"Using SSID: {ssid[:20]}...\n")
    
    # Create API instance
    api = QuotexAPI(ssid=ssid, is_demo=True)
    
    try:
        print("Connecting...")
        await api.connect()
        print("Connected!\n")
        
        # Wait a bit for auth
        await asyncio.sleep(2)
        
        print("Sending test trade...")
        
        # Manually send the exact message format
        trade_data = {
            "asset": "EURUSD",
            "amount": 1,
            "time": 60,
            "action": "call",
            "isDemo": 1,
            "tournamentId": 0,
            "requestId": int(time.time() * 1000),
            "optionType": 100
        }
        
        print(f"Trade data: {trade_data}")
        
        # Send and wait for any responses
        await api.connection.send_socketio_event("orders/open", trade_data)
        
        print("Sent! Waiting for responses...")
        
        # Wait for responses
        await asyncio.sleep(5)
        
        print("\nDone!")
        
    finally:
        await api.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

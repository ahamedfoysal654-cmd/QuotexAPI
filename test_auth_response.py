"""
Test if auth actually works - listen for s_authorization response.
"""

import asyncio
import time
from QuotexAPI import QuotexAPI

received_messages = []

def message_callback(msg):
    print(f"[CALLBACK] Received: {msg[:150]}...")
    received_messages.append(msg)

async def main():
    # Get SSID
    ssid_input = input("Enter SSID: ").strip()
    if ssid_input.startswith('42["authorization"'):
        import json
        auth_data = json.loads(ssid_input[2:])
        ssid = auth_data[1]["session"]
    else:
        ssid = ssid_input
    
    print(f"Using SSID: {ssid[:20]}...\n")
    
    api = QuotexAPI(ssid=ssid, is_demo=True)
    
    try:
        print("Connecting...")
        await api.connect()
        print("Connected!\n")
        
        # Set message callback AFTER connecting
        if api.connection._ws:
            api.connection._ws.set_on_message(message_callback)
        
        print("Waiting for messages (10 seconds)...")
        await asyncio.sleep(10)
        
        print(f"\n{'='*60}")
        print(f"Total messages received: {len(received_messages)}")
        print(f"{'='*60}")
        
        for i, msg in enumerate(received_messages, 1):
            print(f"{i}. {msg[:200]}")
        
        # Check if we got s_authorization
        auth_received = any('s_authorization' in msg for msg in received_messages)
        print(f"\ns_authorization received: {auth_received}")
        
    finally:
        await api.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

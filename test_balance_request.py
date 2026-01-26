"""
Test if balance request works.
"""

import asyncio
import time
from QuotexAPI import QuotexAPI

received_messages = []

def message_callback(msg):
    print(f"[MESSAGE] {msg[:300]}...")
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
        
        # Set message callback to see ALL messages
        if api.connection._ws:
            api.connection._ws.set_on_message(message_callback)
        
        print("Requesting balance...")
        balance = await api.get_balance()
        print(f"Balance returned: ${balance}\n")
        
        print("Waiting a bit more for any late messages...")
        await asyncio.sleep(3)
        
        print(f"\n{'='*60}")
        print(f"Total messages received: {len(received_messages)}")
        print(f"{'='*60}\n")
        
        for i, msg in enumerate(received_messages, 1):
            print(f"{i}. {msg}")
        
        # Check for balance-related messages
        balance_msgs = [msg for msg in received_messages if 'balance' in msg.lower()]
        print(f"\nBalance-related messages: {len(balance_msgs)}")
        for msg in balance_msgs:
            print(f"  - {msg[:200]}")
        
    finally:
        await api.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

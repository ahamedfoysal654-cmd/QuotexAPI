"""
Test Socket.IO with HTTP polling (not WebSocket).
"""

import requests
import json
import time

# Socket.IO HTTP polling endpoint
base_url = "https://ws2.qxbroker.com/socket.io/"

# Headers matching browser
headers = {
    'Origin': 'https://qxbroker.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
    'Referer': 'https://qxbroker.com/',
}

print("1. Opening Socket.IO session (HTTP polling)...")
# Open session with EIO=3 (Engine.IO v3) and transport=polling
params = {
    'EIO': '3',
    'transport': 'polling',
    't': str(int(time.time() * 1000))
}

response = requests.get(base_url, params=params, headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

if response.status_code == 200:
    # Parse handshake to get sid
    handshake = response.text
    if handshake.startswith('0{'):
        handshake_data = json.loads(handshake[1:])
        sid = handshake_data['sid']
        print(f"Got SID: {sid}")
        
        # 2. Send namespace connect
        print("\n2. Connecting to namespace...")
        params['sid'] = sid
        # Send "40" (namespace connect)
        post_response = requests.post(base_url, params=params, headers=headers, data='40')
        print(f"Status: {post_response.status_code}")
        
        # 3. Poll for messages
        print("\n3. Polling for messages...")
        poll_response = requests.get(base_url, params=params, headers=headers)
        print(f"Response: {poll_response.text}")
        
        # 4. Send authorization
        print("\n4. Sending authorization...")
        ssid = "op86rXkNQhMwqhlhScd45R4xlIbN2CnHRlelpFCw"
        auth_msg = '42' + json.dumps(["authorization", {"session": ssid, "isDemo": 1, "tournamentId": 0}])
        auth_response = requests.post(base_url, params=params, headers=headers, data=auth_msg)
        print(f"Status: {auth_response.status_code}")
        
        # 5. Poll again
        print("\n5. Polling after auth...")
        poll_response = requests.get(base_url, params=params, headers=headers)
        print(f"Response: {poll_response.text}")
        
        # 6. Send trade
        print("\n6. Sending trade...")
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
        trade_msg = '42' + json.dumps(["orders/open", trade_data])
        trade_response = requests.post(base_url, params=params, headers=headers, data=trade_msg)
        print(f"Status: {trade_response.status_code}")
        print(f"Response: {trade_response.text}")
        
        # 7. Poll for trade response
        print("\n7. Polling for trade response...")
        for i in range(5):
            poll_response = requests.get(base_url, params=params, headers=headers)
            print(f"Poll {i+1}: {poll_response.text[:200]}")
            if poll_response.text and len(poll_response.text) > 5:
                break
            time.sleep(0.5)
        
    else:
        print("Unexpected handshake format")
else:
    print(f"Failed to connect: {response.text}")

"""Debug Socket.IO polling session behavior"""
from curl_cffi import requests
import time
import re

session = requests.Session(impersonate="chrome110")

url = "https://ws2.qxbroker.com/socket.io/?EIO=3&transport=polling"
headers = {
    'Origin': 'https://qxbroker.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
}

print("Step 1: Handshake")
r1 = session.get(url, headers=headers, timeout=10)
print(f"Status: {r1.status_code}")
print(f"Response: {r1.text[:200]}")

if r1.status_code == 200:
    match = re.search(r'"sid":"([^"]+)"', r1.text)
    if match:
        sid = match.group(1)
        print(f"SID: {sid}")
        
        print("\nStep 2: Immediate second poll (no delay)")
        url_with_sid = f"{url}&sid={sid}"
        r2 = session.get(url_with_sid, headers=headers, timeout=5)
        print(f"Status: {r2.status_code}")
        print(f"Response: {r2.text[:200] if r2.text else '(empty)'}")
        
        if r2.status_code == 400:
            print("\n❌ Session invalid immediately after handshake")
            print("This suggests the server doesn't recognize this SID")
        elif r2.status_code == 200:
            print("\n✅ Polling works!")
            
            print("\nStep 3: Try to send a message")
            msg = '2probe'
            r3 = session.post(url_with_sid, headers={**headers, 'Content-Type': 'text/plain;charset=UTF-8'}, 
                            data=msg, timeout=10)
            print(f"Send status: {r3.status_code}")
            print(f"Send response: {r3.text[:200] if r3.text else '(empty)'}")

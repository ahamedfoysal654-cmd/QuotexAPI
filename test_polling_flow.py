"""Manual test of Socket.IO polling flow"""
from curl_cffi import requests
import time

print("Testing Socket.IO polling flow...")

session = requests.Session(impersonate="chrome110")

base_url = "https://ws2.qxbroker.com/socket.io/"
headers = {
    'Origin': 'https://qxbroker.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
}

# Step 1: Handshake
print("\n=== STEP 1: Handshake (GET) ===")
url1 = f"{base_url}?EIO=3&transport=polling"
print(f"URL: {url1}")
r1 = session.get(url1, headers=headers, timeout=10)
print(f"Status: {r1.status_code}")
print(f"Response: {r1.text[:300]}")
print(f"Cookies: {dict(r1.cookies)}")
print(f"Session cookies: {dict(session.cookies)}")

if r1.status_code != 200:
    print("FAILED at handshake")
    exit(1)

# Extract SID
import re
match = re.search(r'"sid":"([^"]+)"', r1.text)
if not match:
    print("ERROR: No SID found")
    exit(1)

sid = match.group(1)
print(f"\nGot SID: {sid}")

# Step 2: Immediate poll with SID
print("\n=== STEP 2: First poll with SID (GET) ===")
url2 = f"{base_url}?EIO=3&transport=polling&sid={sid}"
print(f"URL: {url2}")
time.sleep(0.5)  # Small delay
r2 = session.get(url2, headers=headers, timeout=10)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text[:300]}")

# Step 3: Send something
if r2.status_code == 200:
    print("\n=== STEP 3: Send test message (POST) ===")
    test_msg = '2probe'  # Ping message
    print(f"Sending: {test_msg}")
    r3 = session.post(url2, headers={**headers, 'Content-Type': 'text/plain;charset=UTF-8'}, 
                      data=test_msg, timeout=10)
    print(f"Status: {r3.status_code}")
    print(f"Response: {r3.text[:200]}")

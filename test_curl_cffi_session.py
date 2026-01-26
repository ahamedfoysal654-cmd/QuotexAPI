"""Test curl_cffi session with Socket.IO polling"""
from curl_cffi import requests

print("Creating session with chrome110 impersonation...")
session = requests.Session(impersonate="chrome110")

url = "https://ws2.qxbroker.com/socket.io/?EIO=3&transport=polling"
headers = {
    'Origin': 'https://qxbroker.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': '*/*',
}

print(f"\n1. Initial GET handshake...")
print(f"URL: {url}")
response1 = session.get(url, headers=headers, timeout=10)
print(f"Status: {response1.status_code}")
print(f"Response: {response1.text[:200]}")
print(f"Cookies: {dict(response1.cookies)}")

# Extract SID
import re
match = re.search(r'"sid":"([^"]+)"', response1.text)
if match:
    sid = match.group(1)
    print(f"SID: {sid}")
    
    # Try posting with SID
    print(f"\n2. POST with SID...")
    post_url = f"{url}&sid={sid}"
    print(f"URL: {post_url}")
    response2 = session.post(post_url, headers=headers, data="", timeout=10)
    print(f"Status: {response2.status_code}")
    print(f"Response: {response2.text[:200]}")
    
    # Try polling
    print(f"\n3. GET with SID...")
    response3 = session.get(post_url, headers=headers, timeout=10)
    print(f"Status: {response3.status_code}")
    print(f"Response: {response3.text[:200]}")
else:
    print("ERROR: Could not extract SID")

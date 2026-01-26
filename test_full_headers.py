"""Test curl_cffi with matching User-Agent"""
from curl_cffi import requests

session = requests.Session(impersonate="chrome110")

url = "https://ws2.qxbroker.com/socket.io/?EIO=3&transport=polling"

# Chrome 110 User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://qxbroker.com',
    'Referer': 'https://qxbroker.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
}

print("Attempting connection with full Chrome 110 headers...")
print(f"URL: {url}")

try:
    r = session.get(url, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
    print(f"Headers: {dict(r.headers)}")
except Exception as e:
    print(f"Error: {e}")

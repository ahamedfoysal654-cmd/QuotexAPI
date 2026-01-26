"""Test if curl_cffi maintains cookies across requests"""
from curl_cffi import requests
import time

print("Testing curl_cffi session...")

# Create session
session = requests.Session(impersonate="chrome110")

# First request to set cookies
url = "https://httpbin.org/cookies/set?test=value123"
print(f"\n1. Setting cookie...")
r1 = session.get(url)
print(f"Cookies after set: {dict(r1.cookies)}")

# Second request to see if cookie persists
url2 = "https://httpbin.org/cookies"
print(f"\n2. Reading cookies...")
r2 = session.get(url2)
print(f"Response: {r2.text}")

# Check session cookies
print(f"\n3. Session cookies: {dict(session.cookies)}")

# Cloudflare Bot Protection Issue

## Problem

Quotex's WebSocket endpoint (`wss://ws2.qxbroker.com`) is protected by **Cloudflare Bot Management**, which blocks standard Python WebSocket libraries (`websockets`, `websocket-client`, `python-socketio`) with **HTTP 403 Forbidden** errors.

### What Works
✅ **Browser** - Full WebSocket connection works  
✅ **curl command-line** - Can connect and receive messages  
❌ **Python websockets library** - Blocked by Cloudflare  
❌ **Python websocket-client** - Blocked by Cloudflare  
❌ **Python socketio** - Blocked by Cloudflare  

## Why This Happens

Cloudflare's bot detection analyzes:
1. **TLS fingerprints** - Python libraries have different TLS signatures than browsers
2. **HTTP headers** - Missing browser-specific headers (Sec-CH-UA, etc.)
3. **Request patterns** - Bot-like behavior triggers challenges
4. **JavaScript challenges** - Requires JavaScript execution (Python can't do this)

## Solutions

### Solution 1: Use Authenticated Session from Browser (RECOMMENDED)

The SSID token you get from the browser is already authenticated and should work once you get past Cloudflare.

**Steps:**
1. Log into qxbroker.com in your browser
2. Open DevTools → Network tab → Filter: WS
3. Find the WebSocket connection
4. Copy the **full authorization message**:
   ```
   42["authorization",{"session":"YOUR_TOKEN_HERE","isDemo":1,"tournamentId":0}]
   ```
5. Use this with the API

**Problem:** Still blocked at connection time by Cloudflare

### Solution 2: Browser Automation with Playwright (BEST)

Use Playwright to automate a real browser, which bypasses Cloudflare completely.

**Install:**
```bash
pip install playwright
playwright install chromium
```

**Example:**
```python
import asyncio
from playwright.async_api import async_playwright

async def get_websocket_connection():
    async with async_playwright() as p:
        # Launch real browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to Quotex
        await page.goto('https://qxbroker.com')
        
        # Wait for user to log in manually or automate login
        input("Press Enter after logging in...")
        
        # Listen for WebSocket
        async with page.expect_websocket() as ws_info:
            ws = await ws_info.value
            
            # Now you have a real WebSocket connection
            # that bypasses Cloudflare!
            
            async def on_frame(frame):
                print(f"Received: {frame}")
            
            ws.on("framereceived", on_frame)
            
            # Send messages
            ws.send('42["authorization",{...}]')
            
            await page.wait_for_timeout(30000)
        
        await browser.close()

asyncio.run(get_websocket_connection())
```

### Solution 3: Proxy Through Authenticated Browser

Run a local proxy server that forwards requests through an authenticated browser session.

### Solution 4: Use curl_cffi (Experimental)

The `curl_cffi` library uses libcurl and can impersonate browsers better:

```python
from curl_cffi import requests
from curl_cffi.requests import Session

# This might work better than standard libraries
session = Session(impersonate="chrome110")
```

However, WebSocket support in curl_cffi is still experimental.

### Solution 5: Get Cloudflare Bypass Token

Some services provide Cloudflare bypass tokens/cookies that you can use with Python requests.

## Current Test Results

### Working: curl Command
```bash
curl "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket" \
  -H "User-Agent: Mozilla/5.0..." \
  -H "Origin: https://qxbroker.com" \
  -H "Upgrade: websocket" \
  -H "Connection: Upgrade" \
  -H "Sec-WebSocket-Key: ..." \
  -H "Sec-WebSocket-Version: 13"
```

**Response:**
```
0{"sid":"HiBqlrMABU7mko6ZemUS","upgrades":[],"pingInterval":25000,"pingTimeout":5000}
40
```

### Not Working: Python Libraries

All Python WebSocket libraries receive:
```
HTTP 403 Forbidden
cf-mitigated: challenge
Content: "Just a moment... Enable JavaScript and cookies to continue"
```

## Recommended Approach for This Library

### Option A: Browser Automation (Most Reliable)

Integrate Playwright for connection establishment:

```python
from quotexapi import QuotexAPI

# Uses Playwright under the hood
api = QuotexAPI(use_browser=True)
await api.connect()  # Opens browser, bypasses Cloudflare
await api.login_with_ssid(ssid)
```

### Option B: Manual SSID + Cookie Injection

Require users to get SSID + Cloudflare cookies from browser:

```python
api = QuotexAPI()
api.set_cloudflare_cookies({
    '__cf_bm': 'xxx...',
    'cf_clearance': 'xxx...'
})
await api.connect()
await api.login_with_ssid(ssid)
```

### Option C: curl Subprocess (Hacky but Works)

Use curl as transport layer (already tested, works!):

```python
api = QuotexAPI(transport='curl')  # Uses curl subprocess
await api.connect()
```

## Testing

Run tests to see the Cloudflare protection in action:

```bash
# Shows curl works
python tests/test_curl_websocket.py

# Shows Python libraries blocked
python tests/test_socketio_flow.py
python tests/test_websocket_client.py
python tests/test_python_socketio.py
```

## Next Steps

1. **Implement Playwright integration** - Most reliable solution
2. **Add curl fallback** - Works but not ideal for production
3. **Document cookie extraction** - Let users provide Cloudflare cookies
4. **Add retry logic** - Try multiple approaches automatically

## References

- [Cloudflare Bot Management](https://www.cloudflare.com/products/bot-management/)
- [Playwright Python](https://playwright.dev/python/)
- [curl_cffi](https://github.com/yifeikong/curl_cffi)

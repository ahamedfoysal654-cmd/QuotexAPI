# How to Get Your Quotex SSID Token

The SSID (Session ID) is required to authenticate with the Quotex WebSocket API. Here's how to obtain it:

## Method 1: From Browser (Recommended)

1. **Open Quotex in your browser**
   - Go to https://qxbroker.com
   - Log in to your account

2. **Open Browser Developer Tools**
   - Press `F12` or right-click and select "Inspect"
   - Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)

3. **Find the SSID Cookie**
   - In the left sidebar, expand **Cookies**
   - Click on `https://qxbroker.com`
   - Look for a cookie named `ssid`
   - Copy the **Value** (should be a long alphanumeric string)

4. **Example SSID Format**
   ```
   dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH
   ```

## Method 2: From Network Tab

1. **Open Developer Tools** (F12)
2. Go to **Network** tab
3. **Refresh the page** or perform any action
4. Look for WebSocket connections (filter by `WS`)
5. Check the connection URL - it may include `ssid=...` parameter
6. Copy just the SSID value

## Method 3: Programmatic Login (Future)

In the future, the API will support email/password login which will automatically obtain and manage the SSID for you:

```python
from QuotexAPI import QuotexAPI

api = QuotexAPI()
await api.connect()
await api.login_with_email("your@email.com", "your_password")
# SSID will be automatically obtained and used
```

## Using the SSID

### Environment Variable (Recommended)
```bash
export QUOTEX_SSID='your_ssid_token_here'
python examples/get_balance.py
```

### Programmatically
```python
from QuotexAPI import QuotexAPI

api = QuotexAPI(ssid="your_ssid_token_here")
await api.connect()
```

### In Examples
```python
import os
from QuotexAPI import QuotexAPI

ssid = os.getenv("QUOTEX_SSID")
api = QuotexAPI()
await api.connect(ssid=ssid)
```

## Important Notes

1. **SSID Expiration**: SSID tokens expire after some time (usually hours/days). You'll need to get a new one when it expires.

2. **Security**: Never commit your SSID to version control. Always use environment variables or secure configuration.

3. **Format**: The SSID should be ONLY the token value, NOT the full Socket.IO authorization message.
   - ✅ Correct: `dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH`
   - ❌ Wrong: `42["authorization",{"session":"dJzh...","isDemo":1}]`

4. **Testing**: After obtaining an SSID, test it quickly as it may expire if not used.

## Troubleshooting

### HTTP 403 Error
- SSID is missing or invalid
- SSID format is incorrect
- Solution: Get a fresh SSID from your browser

### HTTP 502 Error
- SSID may be expired
- Quotex server might be temporarily down
- Solution: Try getting a fresh SSID or wait a few minutes

### "Not authenticated" errors
- SSID is valid but not yet authorized
- Solution: Make sure to call `login_with_ssid()` after connecting

## Security Best Practices

1. Store SSID in environment variables
2. Don't share your SSID with anyone
3. Don't commit SSID to git repositories
4. Rotate SSID regularly for security
5. Use `.env` file for local development (add to `.gitignore`)

```bash
# .env file
QUOTEX_SSID=your_ssid_token_here
```

```python
# Load from .env
from dotenv import load_dotenv
load_dotenv()
```

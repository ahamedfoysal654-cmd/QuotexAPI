# QuotexAPI - Examples Quick Reference

All examples now accept the **full SSID format** from your browser! You can paste the entire value and it will automatically extract just the session token.

## Running Examples

### 1. Get Balance
```bash
python examples/get_balance.py
```

When prompted, paste either:
- **Full format**: `42["authorization",{"session":"dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH","isDemo":1,"tournamentId":0}]`
- **Token only**: `dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH`

Both formats work! The example will automatically extract the token.

### 2. Get Real-time Candles
```bash
python examples/get_candles.py
```

Same SSID format - paste the full value from browser.

### 3. Place Order
```bash
python examples/place_order.py
```

Same SSID format - paste the full value from browser.

## Using Environment Variable

Set once and all examples will use it:
```bash
# You can set the full format or just the token
export QUOTEX_SSID='42["authorization",{"session":"dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH","isDemo":1,"tournamentId":0}]'

# Or just the token
export QUOTEX_SSID='dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH'

# Then run any example
python examples/get_balance.py
```

## How to Get SSID from Browser

1. Open https://qxbroker.com and login
2. Press **F12** to open Developer Tools
3. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Expand **Cookies** → Click on `https://qxbroker.com`
5. Find the `ssid` cookie
6. **Copy the entire Value** - you can paste it directly into any example!

The examples will automatically extract just the session token part.

## Example Outputs

### Get Balance
```
SSID: 42["authorization",{"session":"dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH","isDemo":1,"tournamentId":0}]
✓ Extracted SSID token: dJzhzzKSR6N4Lr5Ov...
🔌 Connecting to Quotex WebSocket...
✅ Connected successfully (received handshake)
🔐 Authenticating with SSID...
✅ Authenticated successfully

💰 Fetching account balances...

==================================================
ACCOUNT BALANCES
==================================================
Demo Account:  $10,000.00
Real Account:  $0.00
==================================================
```

### Get Candles
```
✓ Extracted SSID token: dJzhzzKSR6N4Lr5Ov...
🔌 Connecting to Quotex...
✅ Connected successfully
🔐 Authenticating with SSID...
✅ Authenticated successfully

📈 Subscribing to candle data for 3 assets...
   - EURUSD
   - GBPUSD
   - BTCUSD

✅ Subscriptions active
============================================================
Listening for real-time candle updates...
Press Ctrl+C to stop
============================================================

📊 EURUSD_otc @ 2025-11-27 20:15:00
   Open:   1.05234
   High:   1.05245
   Low:    1.05230
   Close:  1.05238
   Volume: 1234
```

### Place Order
```
✓ Extracted SSID token: dJzhzzKSR6N4Lr5Ov...
🔌 Connecting to Quotex...
✅ Connected successfully
🔐 Authenticating with SSID...
✅ Authenticated successfully

💰 Checking account balance...
   Demo: $10,000.00
   Real: $0.00

============================================================
TRADE PARAMETERS
============================================================
Asset:     EURUSD
Direction: CALL
Amount:    $1.0
Expiry:    60 seconds
Account:   DEMO
============================================================

⚠️  Place this trade? (yes/no): yes

📤 Placing trade...

✅ Trade placed successfully!
```

## Features

- ✅ Accepts full SSID format from browser
- ✅ Automatically extracts session token
- ✅ Works with environment variable
- ✅ Clear visual feedback
- ✅ Proper error handling
- ✅ User-friendly prompts

## Notes

- SSID tokens expire after some time (usually hours)
- Get a fresh SSID from your browser when needed
- All examples use **demo account** by default for safety
- Press **Ctrl+C** to stop streaming examples

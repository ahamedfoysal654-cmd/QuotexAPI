# Quotex Message Formats

This document describes the actual message formats used by the Quotex platform, based on real-world observations.

## Socket.IO Protocol

Quotex uses Socket.IO over WebSocket. All application messages use the format:
```
42["event_name", data]
```

Where:
- `42` = Socket.IO event message type
- `"event_name"` = The event identifier
- `data` = The payload (can be string, object, or array)

## Authentication

### Login Request
```javascript
42["authorization", {
    "session": "your_ssid_token",
    "isDemo": 1,           // 1 for demo, 0 for real
    "tournamentId": 0
}]
```

### Response
After successful authentication, you receive various events including balance updates.

## Account Management

### Balance Update Event
Received automatically after authentication and during trading:

```javascript
42["balance", {
    "liveBalance": 0,
    "demoBalance": 10000,
    "tournamentsBalances": {},
    "dayLimit": 0,
    "dayBalance": 0
}]
```

**Important Fields:**
- `demoBalance` - Demo account balance (NOT `demo_balance`)
- `liveBalance` - Real account balance (NOT `real_balance`)
- `tournamentsBalances` - Tournament balances object
- `dayLimit` - Daily trading limit
- `dayBalance` - Today's balance change

## Trading

### Place Order Request
```javascript
42["orders/open", {
    "asset": "CHFJPY_otc",      // Asset with _otc suffix
    "amount": 1,                 // Trade amount in USD
    "time": 60,                  // Expiry time in seconds (NOT "expiry")
    "action": "call",            // "call" or "put" (NOT "direction")
    "isDemo": 1,                 // 1 for demo, 0 for real
    "tournamentId": 0,           // 0 for regular trading
    "requestId": 1764266241,     // Unique request ID (timestamp-based)
    "optionType": 100            // Binary option type
}]
```

**Critical Differences from Generic API:**
- Event name is `orders/open` (not `place_trade`)
- Use `"action": "call"` or `"action": "put"` (not `direction`)
- Use `"time": 60` (not `expiry`)
- Must include `requestId` for tracking
- Must include `optionType: 100` for binary options
- Asset names require `_otc` suffix

### Order Response
The response to orders/open includes:
```javascript
{
    "id": "order_id",           // or "orderId"
    "isSuccessful": true,       // Success indicator
    "message": "...",           // Error message if failed
    "openPrice": 123.456,       // or "open_price"
    "percent": 85.0,            // Payout percentage
    "requestId": 1764266241     // Matches request
}
```

## Data Streaming

### Subscribe to Candles/Depth
```javascript
42["depth/follow", "EURNZD_otc"]
```

**Note:** 
- Data is just the asset string (not an object)
- Asset must have `_otc` suffix
- No timeframe parameter in subscription (handled server-side)

### Unsubscribe from Candles/Depth
```javascript
42["depth/unfollow", "EURNZD_otc"]
```

### Depth/Candle Updates
Received as `depth` events:
```javascript
42["depth", {
    "asset": "EURNZD_otc",
    "time": 1234567890,
    "open": 1.2345,
    "high": 1.2350,
    "low": 1.2340,
    "close": 1.2347,
    "volume": 1000
    // ... other fields
}]
```

### Real-time Quotes/Ticks
May be received as `tick` events:
```javascript
42["tick", {
    "asset": "EURNZD_otc",
    "time": 1234567890,
    "price": 1.2347,
    "bid": 1.2346,
    "ask": 1.2348
}]
```

## Asset Naming Convention

All asset symbols must include the `_otc` suffix:
- ✅ `"EURUSD_otc"`
- ✅ `"CHFJPY_otc"`
- ✅ `"BTCUSD_otc"`
- ❌ `"EURUSD"` (will not work)

## Field Naming Conventions

Quotex uses mixed conventions:
- **camelCase** for most fields: `isDemo`, `demoBalance`, `liveBalance`, `requestId`
- **snake_case** sometimes: `open_price` (in some responses)
- Our API normalizes these internally

## Request ID Generation

Generate request IDs using high-precision timestamp:
```python
import asyncio
request_id = int(asyncio.get_event_loop().time() * 1000000) % 10000000000
```

This creates a unique 10-digit number suitable for tracking requests.

## Implementation Notes

### In QuotexAPI

1. **ConnectionService** (`services/connection.py`):
   - Handles Socket.IO message parsing and formatting
   - Routes events to appropriate handlers
   - `send_socketio_event()` for sending formatted messages

2. **AuthService** (`services/auth.py`):
   - Uses `42["authorization", {...}]` format
   - Handles SSID authentication

3. **AccountService** (`services/account.py`):
   - Subscribes to `"balance"` event
   - Parses `demoBalance` and `liveBalance` fields

4. **TradingService** (`services/trading.py`):
   - Sends `42["orders/open", {...}]` format
   - Generates unique `requestId` per trade
   - Subscribes to `"orders/open"` event for responses
   - Adds `_otc` suffix to assets automatically

5. **DataService** (`services/data.py`):
   - Sends `42["depth/follow", "ASSET_otc"]` for subscriptions
   - Subscribes to `"depth"` and `"tick"` events
   - Adds `_otc` suffix to assets automatically

## Testing

To verify these formats with real Quotex:

```python
from QuotexAPI import QuotexAPI

async def test_quotex():
    api = QuotexAPI()
    
    # Login
    await api.connect()
    await api.login_with_ssid("your_ssid_token")
    
    # Get balance
    balances = await api.get_balances()
    print(f"Demo: ${balances['demo']}, Real: ${balances['real']}")
    
    # Place trade
    trade = await api.place_trade(
        asset="EURUSD",  # Will be converted to EURUSD_otc
        direction="call",
        amount=1,
        expiry=60
    )
    
    # Subscribe to data
    await api.subscribe_candles("BTCUSD")  # Will be converted to BTCUSD_otc
    
    await api.disconnect()
```

Monitor the actual WebSocket messages to verify formats match exactly.

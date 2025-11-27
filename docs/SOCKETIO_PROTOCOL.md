# Quotex Socket.IO Protocol Format

## Overview

Quotex uses **Socket.IO** protocol for WebSocket communication, not plain JSON. This means all messages follow a specific format with message type codes.

## Socket.IO Message Format

### General Format
```
<message_type_code><json_payload>
```

### Common Message Type Codes

- `0` - Handshake/Open
  - Example: `0{"sid":"abc123","upgrades":[],"pingInterval":25000,"pingTimeout":60000}`
  - Contains session ID (sid) and connection parameters

- `2` - Ping
  - Client sends: `2`
  - Keep-alive mechanism

- `3` - Pong  
  - Server responds: `3`
  - Response to ping

- `40` - Connect to namespace
  - Establishes connection to Socket.IO namespace

- `42` - Event message
  - **This is the main message type for data**
  - Format: `42["event_name", data]`

## Quotex-Specific Messages

### 1. Authorization (SSID Login)

**Format:**
```
42["authorization",{"session":"<SSID>","isDemo":1,"tournamentId":0}]
```

**Example:**
```
42["authorization",{"session":"dJzhzzKSR6N4Lr5OvTFuvcGLCfyDjtdbNDMScXcH","isDemo":1,"tournamentId":0}]
```

**Parameters:**
- `session` (string) - The SSID token
- `isDemo` (int) - 1 for demo account, 0 for real account
- `tournamentId` (int) - Tournament ID, typically 0

**Response:**
Server sends an event (likely `authorization` or `auth_response`) with:
```json
{
  "isSuccessful": true,
  "userId": "12345",
  "demoBalance": 10000.0,
  "realBalance": 0.0,
  ...
}
```

### 2. Place Trade

**Format:**
```
42["place_trade",{"asset":"EURUSD","direction":"call","amount":100,"expiry":60}]
```

**Parameters:**
- `asset` (string) - Trading pair (e.g., "EURUSD", "GBPUSD")
- `direction` (string) - "call" or "put"
- `amount` (float) - Trade amount in USD
- `expiry` (int) - Expiration time in seconds

### 3. Subscribe to Candles

**Format:**
```
42["subscribe_candles",{"asset":"EURUSD","timeframe":60}]
```

**Parameters:**
- `asset` (string) - Trading pair
- `timeframe` (int) - Candle timeframe in seconds (60, 300, etc.)

### 4. Real-time Updates

**Trade Result Event:**
```
42["trade_result",{"orderId":"12345","result":"win","profit":85.0,"closePrice":1.0855}]
```

**Candle Update Event:**
```
42["candle",{"asset":"EURUSD","timestamp":1732723200,"open":1.0850,"high":1.0855,"low":1.0848,"close":1.0852}]
```

**Balance Update Event:**
```
42["balance_update",{"demoBalance":10085.0,"realBalance":0.0,"activeAccount":"demo"}]
```

## Implementation in QuotexAPI

### Sending Messages

```python
# Format the message in Socket.IO format
message = f'42["authorization",{{"session":"{ssid}","isDemo":1,"tournamentId":0}}]'
await websocket.send(message)

# Or use the helper method:
await connection.send_socketio_event(
    event="authorization",
    data={"session": ssid, "isDemo": 1, "tournamentId": 0}
)
```

### Receiving Messages

```python
# Raw message: 42["trade_result",{"orderId":"123","result":"win"}]

# Parse it:
if message.startswith("42"):
    json_part = message[2:]  # Remove "42" prefix
    payload = json.loads(json_part)  # Parse JSON array
    event_name = payload[0]  # "trade_result"
    event_data = payload[1]  # {"orderId":"123","result":"win"}
```

### Connection Flow

```
1. Client connects to WebSocket
   → wss://quotex.io/socket.io/?EIO=4&transport=websocket

2. Server sends handshake
   ← 0{"sid":"abc123",...}

3. Client acknowledges
   → 40

4. Client sends authorization
   → 42["authorization",{"session":"...","isDemo":1,"tournamentId":0}]

5. Server responds with authorization result
   ← 42["authorization",{"isSuccessful":true,...}]

6. Server sends periodic pings
   ← 2

7. Client responds with pongs
   → 3

8. Client subscribes to data
   → 42["subscribe_candles",{"asset":"EURUSD","timeframe":60}]

9. Server pushes real-time updates
   ← 42["candle",{...}]
   ← 42["trade_result",{...}]
```

## Key Differences from Plain JSON

| Aspect | Plain JSON/WebSocket | Socket.IO (Quotex) |
|--------|---------------------|-------------------|
| **Message Format** | `{"msg":"login","data":{...}}` | `42["login",{...}]` |
| **Event Name** | In message body | First element of array |
| **Data** | In message body | Second element of array |
| **Handshake** | Not needed | Required (`0`, `40`) |
| **Keep-alive** | Application-level | Protocol-level (`2`/`3`) |

## Testing

### Example SSID Authorization

```python
import asyncio
import websockets
import json

async def test_quotex_auth():
    uri = "wss://quotex.io/socket.io/?EIO=4&transport=websocket"
    
    async with websockets.connect(uri) as ws:
        # 1. Receive handshake
        handshake = await ws.recv()
        print(f"Handshake: {handshake}")
        # Output: 0{"sid":"...","upgrades":[],...}
        
        # 2. Send connection acknowledgment
        await ws.send("40")
        
        # 3. Send authorization
        ssid = "your_ssid_here"
        auth_msg = f'42["authorization",{{"session":"{ssid}","isDemo":1,"tournamentId":0}}]'
        await ws.send(auth_msg)
        print(f"Sent: {auth_msg}")
        
        # 4. Receive response
        response = await ws.recv()
        print(f"Response: {response}")
        # Output: 42["authorization",{"isSuccessful":true,...}]

asyncio.run(test_quotex_auth())
```

## Important Notes

1. **Message Type 42 is for events**: All application-level messages use `42["event", data]` format

2. **Keep-alive**: Socket.IO handles ping/pong automatically (messages `2` and `3`)

3. **Event Names**: The first element in the array after `42` is the event name
   - Examples: `"authorization"`, `"place_trade"`, `"candle"`, `"trade_result"`

4. **Data Payload**: The second element is the data object
   - Can be any JSON-serializable structure

5. **No request_id needed**: Socket.IO events are fire-and-forget unless you implement your own correlation

6. **Responses are events**: The server responds by sending another event (not a direct response)
   - You need to subscribe to the response event before sending your request

## Updated Architecture

```
Client                                      Server
  │                                           │
  ├─ Connect WebSocket                        │
  │  ────────────────────────────────────────►│
  │                                           │
  │◄──── Handshake: 0{"sid":"..."}  ─────────┤
  │                                           │
  ├─ Connect: 40                              │
  │  ────────────────────────────────────────►│
  │                                           │
  ├─ 42["authorization",{...}]                │
  │  ────────────────────────────────────────►│
  │                                           │
  │◄──── 42["authorization",{...}]  ─────────┤
  │                                           │
  ├─ 42["subscribe_candles",{...}]            │
  │  ────────────────────────────────────────►│
  │                                           │
  │◄──── 42["candle",{...}]  ────────────────┤
  │◄──── 42["candle",{...}]  ────────────────┤
  │                                           │
  ├─ Ping: 2                                  │
  │  ────────────────────────────────────────►│
  │                                           │
  │◄──── Pong: 3  ───────────────────────────┤
```

## Summary

Quotex uses Socket.IO protocol which requires:
- ✅ Parsing message type codes (`0`, `2`, `3`, `40`, `42`)
- ✅ Formatting events as `42["event_name", data]`
- ✅ Handling Socket.IO handshake
- ✅ Responding to ping/pong
- ✅ Subscribing to events before sending requests
- ✅ Event-based responses (not request/response)

The QuotexAPI `ConnectionService` now handles all of this automatically!

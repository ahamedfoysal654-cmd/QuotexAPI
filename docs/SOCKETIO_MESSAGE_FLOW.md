# Socket.IO Message Flow - Quotex API

This document describes the actual Socket.IO message flow observed from network traffic.

## Connection Details

**WebSocket URL:** `wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket`

**Required Headers:**
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36
Origin: https://qxbroker.com
Cache-Control: no-cache
Pragma: no-cache
Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7
```

## Socket.IO Protocol Basics

### Message Type Codes

| Code | Type | Description |
|------|------|-------------|
| `0` | Handshake | Initial connection with session details |
| `2` | Ping | Server ping (respond with `3`) |
| `3` | Pong | Client pong response |
| `40` | Namespace Connect | Connected to namespace |
| `41` | Namespace Disconnect | Disconnected from namespace |
| `42` | Event | Event with data `42["event_name", data]` |
| `43` | Ack | Acknowledgment without data |
| `451-459` | Ack with Data | Acknowledgment with response data |

## Connection Sequence

### 1. Initial Handshake

**Server sends:**
```
0{"sid":"...","upgrades":[],"pingInterval":25000,"pingTimeout":5000}
```

**Example:**
```json
{
  "sid": "op86rXkNQiMwqlh...",
  "upgrades": [],
  "pingInterval": 25000,
  "pingTimeout": 5000
}
```

### 2. Namespace Connection

**Server sends:**
```
40
```
This indicates the client is connected to the default namespace.

### 3. Authorization

**Client sends:**
```
42["authorization",{"session":"YOUR_SSID_TOKEN"}]
```

**Server responds:**
```
451-[{"authorization":"success"}]
```

## Common API Messages

### Get Instruments List

**Request:**
```
42["instruments/list",{"_placeholder":true,"num":0}]
```

**Response:**
```
451-[{"instruments":[...]}]
```

### Get Balance

**Request:**
```
42["s_balance/list",{"_placeholder":true,"num":0}]
```

**Response:**
```
451-[{"balance":...}]
```

### Get Settings

**Request:**
```
42["settings/list",{"_placeholder":true,"num":0}]
```

**Response:**
```
451-[{"settings":{...}}]
```

### Get Pending Trades

**Request:**
```
42["pending/list"]
```

**Response:**
```
451-[{"pending":[...]}]
```

### Get Open Orders

**Request:**
```
42["s_orders/opened/list",{"_placeholder":true,"num":0}]
```

**Response:**
```
451-[{"orders":[...]}]
```

### Get Closed Orders

**Request:**
```
42["s_orders/closed/list",{"_placeholder":true,"num":0}]
```

**Response:**
```
451-[{"orders":[...]}]
```

### Subscribe to Candles

**Request:**
```
42["candles/subscribe",{"asset":"EURUSD","period":60}]
```

### Drawing/Load Operations

**Request:**
```
42["s_drawing/load",{"_placeholder":true,"num":0}]
```

**Response:**
```
451-[{"drawings":[...]}]
```

### Update Operations

**Request:**
```
42["pending/update",{"asset":"GBPJPY","period":55}]
```

## Binary Messages

Some responses are sent as binary data (shown as "Binary Message" in network traffic). These typically contain:
- Candle data updates
- Real-time quote updates
- Chart data

## Placeholder Pattern

Many requests use a placeholder pattern:
```json
{"_placeholder": true, "num": 0}
```

This appears to be Quotex's convention for requesting list data without filters.

## Ping/Pong Keep-Alive

**Server ping:**
```
2
```

**Client must respond:**
```
3
```

The server sends pings every 25 seconds (based on `pingInterval` from handshake).

## Event Response Format

Events use the format: `42["event_name", data]`

Acknowledgments with data use: `451-[response_array]` where the number after `45` can vary.

## Implementation Notes

1. **No SSID in URL**: Unlike some APIs, Quotex doesn't require SSID in the WebSocket URL
2. **Authorization After Connect**: Send authorization as a Socket.IO event after connection
3. **Placeholder Pattern**: Use `{"_placeholder":true,"num":0}` for list requests
4. **Binary Messages**: Handle both text and binary WebSocket frames
5. **Keep-Alive**: Respond to ping (2) with pong (3) to maintain connection

## Example Connection Flow

```python
# 1. Connect to WebSocket
websocket = await websockets.connect(
    "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket",
    extra_headers={...}
)

# 2. Receive handshake: 0{...}
# 3. Receive namespace connect: 40

# 4. Send authorization
await websocket.send('42["authorization",{"session":"YOUR_SSID"}]')

# 5. Wait for auth response: 451-[...]

# 6. Request data
await websocket.send('42["instruments/list",{"_placeholder":true,"num":0}]')
await websocket.send('42["s_balance/list",{"_placeholder":true,"num":0}]')

# 7. Handle incoming messages and respond to pings
async for message in websocket:
    if message == '2':
        await websocket.send('3')  # Respond to ping
    elif message.startswith('42'):
        # Handle event
        pass
    elif message.startswith('451'):
        # Handle acknowledgment
        pass
```

## Testing

Use the test script to verify the connection:

```bash
python tests/test_socketio_flow.py
```

This will show you the actual message sequence from the server.

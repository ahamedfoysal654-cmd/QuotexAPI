# QuotexAPI - WebSocket-Based Architecture Summary

## 🔄 Core Architectural Change

**Everything happens through WebSocket messages** - there is no traditional REST API.

## What Changed

### Before (Typical REST API)
```python
# HTTP POST to /api/login
response = await http_client.post("/api/login", json={"email": ..., "password": ...})

# HTTP POST to /api/trade
trade = await http_client.post("/api/trade", json={"asset": ..., "amount": ...})

# Poll for trade result
while True:
    result = await http_client.get(f"/api/trade/{order_id}")
    if result.status == "closed":
        break
    await asyncio.sleep(1)
```

### After (WebSocket Messages)
```python
# Send login message via WebSocket
response = await connection.send_request("login", {"email": ..., "password": ...})

# Send trade message via WebSocket
response = await connection.send_request("place_trade", {"asset": ..., "amount": ...})

# Receive trade updates automatically via WebSocket events
connection.subscribe("trade_result", lambda data: print(data))
# Updates are pushed in real-time, no polling needed
```

## Architecture Components

### 1. WebSocket Protocol (`ws_protocol.py`)
Defines all message types and structures:
- `LoginRequest`, `PlaceTradeRequest`, etc.
- `AuthResponse`, `TradeResultMessage`, etc.
- Message type enums
- Request/response data classes

### 2. Connection Service (`services/connection.py`)
Core WebSocket management with:
- **Message Routing**: Directs incoming messages to appropriate handlers
- **Request/Response Correlation**: Matches responses to requests using `request_id`
- **Event Subscription**: Allows services to listen for specific message types
- **Auto-reconnect**: Handles disconnections gracefully

```python
# Send request and wait for correlated response
response = await connection.send_request(
    message_type="login",
    data={"email": "...", "password": "..."},
    timeout=30.0
)

# Subscribe to events
connection.subscribe("candle", on_candle_update)
connection.subscribe("trade_result", on_trade_result)
```

### 3. Service Layer
All services (Auth, Trading, Account, Data) use WebSocket messages:

```python
class AuthService:
    def __init__(self, connection: ConnectionService):
        self._connection = connection
    
    async def login(self, email, password):
        response = await self._connection.send_request(
            "login",
            {"email": email, "password": password}
        )
        return parse_response(response)
```

## Message Flow

### Request/Response Pattern
```
Client                             Server
  │                                  │
  ├── send_request("login") ────────►│
  │   request_id: "uuid-123"         │
  │                                  │
  │◄────── response ─────────────────┤
  │        request_id: "uuid-123"    │
  │        success: true             │
```

The `request_id` links request and response together, enabling async request/response over WebSocket.

### Event Pattern
```
Client                             Server
  │                                  │
  ├── subscribe("trade_result") ────►│
  │                                  │
  │◄────── trade_result ─────────────┤ (pushed event)
  │        order_id: "..."           │
  │        result: "win"             │
  │        profit: 85.0              │
  │                                  │
  │◄────── trade_result ─────────────┤ (another event)
  │        order_id: "..."           │
  │        result: "loss"            │
```

## Benefits

### ✅ Real-time by Default
- No polling required for trade results
- Instant price updates
- Immediate balance notifications

### ✅ Efficient
- Single persistent connection
- Low latency
- Reduced overhead

### ✅ Simple for Users
```python
# API looks simple and synchronous
trade = await api.place_trade("EURUSD", "call", 100)

# But behind the scenes, WebSocket messages are sent/received
# and events are automatically routed
```

### ✅ Event-Driven
```python
# Subscribe to any event type
api.subscribe_candles("EURUSD")
api.on_candle(lambda candle: print(candle))

# Real-time data flows automatically
```

## Key Files

| File | Purpose |
|------|---------|
| `ws_protocol.py` | Message definitions (requests, responses, events) |
| `services/connection.py` | WebSocket connection + message routing |
| `services/auth.py` | Login/logout via WebSocket |
| `services/trading.py` | Place/cancel trades via WebSocket |
| `services/data.py` | Stream candles/quotes via WebSocket |
| `services/account.py` | Get/switch balance via WebSocket |

## Example: Complete Trade Flow

```python
from QuotexAPI import QuotexAPI

async def main():
    api = QuotexAPI(email="user@example.com", password="password")
    
    # 1. Connect (establishes WebSocket)
    await api.connect()
    
    # 2. Login (sends "login" message via WebSocket)
    await api.login()
    
    # 3. Subscribe to live candles (sends "subscribe_candles" message)
    api.subscribe_candles("EURUSD", timeframe=60)
    
    # 4. Register event handler
    def on_candle(candle):
        print(f"New candle: {candle['close']}")
    
    api.on_candle("EURUSD", on_candle)
    
    # 5. Place trade (sends "place_trade" message via WebSocket)
    trade = await api.place_trade(
        asset="EURUSD",
        direction="call",
        amount=100,
        expiry=60
    )
    
    # 6. Monitor trade (receives "trade_result" events automatically)
    def on_result(data):
        print(f"Trade result: {data['result']}, profit: {data['profit']}")
    
    api.on_trade_update(trade.order_id, on_result)
    
    # 7. Wait for result (blocks until "trade_result" event received)
    result = await api.wait_for_result(trade.order_id)
    print(f"Final result: {result}")
    
    await api.disconnect()

# Behind the scenes, all of this happens through WebSocket messages:
# - connect() → WebSocket handshake
# - login() → send {"msg": "login", ...} → receive {"msg": "auth_response", ...}
# - subscribe_candles() → send {"msg": "subscribe_candles", ...}
# - place_trade() → send {"msg": "place_trade", ...} → receive response
# - Events flow automatically: {"msg": "candle", ...}, {"msg": "trade_result", ...}
```

## Testing

```python
# Mock WebSocket for testing
class MockConnection:
    async def send_request(self, msg_type, data, timeout=None):
        if msg_type == "login":
            return {"success": True, "ssid": "test_token"}
        elif msg_type == "place_trade":
            return {"success": True, "order_id": "test_order"}

# Test services
auth = AuthService(MockConnection())
result = await auth.login("user@test.com", "password")
assert result.user_id is not None
```

## Documentation

See detailed documentation in:
- **`docs/WEBSOCKET_ARCHITECTURE.md`** - Comprehensive WebSocket architecture guide
- **`docs/ARCHITECTURE.md`** - Overall system architecture
- **`examples/`** - Usage examples

## Summary

QuotexAPI uses a **WebSocket-centric architecture** where:
1. All operations are WebSocket messages (no REST)
2. Connection service routes messages intelligently
3. Request/response correlation via `request_id`
4. Real-time events for data streams and trade updates
5. Clean service layer abstracts WebSocket complexity

This design provides real-time communication, low latency, and an elegant developer experience for a trading platform.

# QuotexAPI - WebSocket Architecture

## 🎯 Key Concept

**QuotexAPI uses WebSocket messages for ALL operations** - there is no traditional REST API. This means:

- Authentication happens via WebSocket messages
- Trading operations send WebSocket messages
- Account management uses WebSocket messages
- Real-time data streams through WebSocket naturally
- Trade results are pushed via WebSocket events

## Why WebSocket-First?

### Traditional REST API Approach ❌
```python
# Login via HTTP
response = requests.post("/api/login", json={...})

# Place trade via HTTP  
trade = requests.post("/api/trade", json={...})

# Poll for result (inefficient!)
while True:
    result = requests.get(f"/api/trade/{id}")
    if result.done:
        break
    time.sleep(1)  # Wasted requests!
```

### WebSocket Approach ✅
```python
# Login via WebSocket message
await api.login()  # Sends WebSocket message

# Place trade via WebSocket message
trade = await api.place_trade(...)  # Sends WebSocket message

# Result pushed automatically (no polling!)
api.on_trade_result(lambda result: print(result))
# Server pushes updates in real-time
```

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│                    QuotexAPI Client                   │
│             (High-level convenience API)              │
└──────────────┬──────────┬──────────┬─────────────────┘
               │          │          │
               ▼          ▼          ▼
         ┌─────────┐ ┌────────┐ ┌─────────┐
         │  Auth   │ │Trading │ │  Data   │
         │ Service │ │Service │ │ Service │
         └────┬────┘ └───┬────┘ └────┬────┘
              │          │           │
              └──────────┴───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Connection Service  │
              │ • Message Routing    │
              │ • Request/Response   │
              │ • Event Distribution │
              │ • Auto-reconnect     │
              └──────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   WebSocket Protocol │
              │  (Single Connection) │
              └──────────────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │Quotex Server │
                  └──────────────┘
```

## How It Works

### 1. Message Correlation

Every request gets a unique ID to match responses:

```python
# Client sends:
{
  "msg": "place_trade",
  "request_id": "uuid-abc-123",
  "asset": "EURUSD",
  "amount": 100
}

# Server responds with same request_id:
{
  "msg": "trade_response",
  "request_id": "uuid-abc-123",
  "success": true,
  "order_id": "order-456"
}
```

The Connection Service automatically matches them.

### 2. Event Subscription

Services and users can subscribe to specific events:

```python
# Subscribe to trade results
connection.subscribe("trade_result", handle_trade_result)

# When server pushes event:
{
  "msg": "trade_result",
  "order_id": "order-456",
  "result": "win",
  "profit": 85.0
}

# Handler is called automatically
```

### 3. Real-time Data Streams

```python
# Subscribe to candles
await api.subscribe_candles("EURUSD", timeframe=60)

# Register handler
api.on_candle("EURUSD", lambda candle: print(candle))

# Candles flow automatically:
# → {"msg": "candle", "asset": "EURUSD", "close": 1.0850, ...}
# → {"msg": "candle", "asset": "EURUSD", "close": 1.0852, ...}
# → {"msg": "candle", "asset": "EURUSD", "close": 1.0851, ...}
```

## Complete Example

```python
import asyncio
from QuotexAPI import QuotexAPI

async def main():
    # Initialize API
    api = QuotexAPI(
        email="your@email.com",
        password="your_password"
    )
    
    # Connect (establishes WebSocket)
    await api.connect()
    print("WebSocket connected")
    
    # Login via WebSocket
    await api.login()
    print("Logged in via WebSocket")
    
    # Subscribe to live candles via WebSocket
    await api.subscribe_candles("EURUSD", timeframe=60)
    
    # Handle candle updates (pushed via WebSocket)
    def on_candle(data):
        print(f"New candle: Close={data['close']}")
    
    api.on_candle("EURUSD", on_candle)
    
    # Place trade via WebSocket
    trade = await api.place_trade(
        asset="EURUSD",
        direction="call",
        amount=100,
        expiry=60
    )
    print(f"Trade placed: {trade.order_id}")
    
    # Monitor trade via WebSocket events
    def on_result(data):
        result = data['result']  # "win" or "loss"
        profit = data['profit']
        print(f"Trade completed: {result}, profit: ${profit}")
    
    api.on_trade_update(trade.order_id, on_result)
    
    # Wait for trade to complete
    # (receives updates via WebSocket automatically)
    result = await api.wait_for_result(trade.order_id)
    print(f"Final result: {result}")
    
    # Cleanup
    await api.disconnect()

asyncio.run(main())
```

## Benefits

| Feature | WebSocket Architecture | Traditional REST |
|---------|----------------------|------------------|
| **Latency** | Low (persistent connection) | Higher (new connection each time) |
| **Real-time** | Native (server push) | Requires polling or separate WebSocket |
| **Efficiency** | 1 connection for everything | N connections |
| **Trade Updates** | Pushed automatically | Must poll repeatedly |
| **Data Streams** | Built-in | Need separate mechanism |
| **Resource Usage** | Minimal | Higher (repeated connections) |

## Message Types

See `QuotexAPI/ws_protocol.py` for complete message definitions:

- **Authentication**: `login`, `logout`, `auth_response`
- **Trading**: `place_trade`, `cancel_trade`, `trade_result`, `trade_update`
- **Account**: `get_balance`, `switch_account`, `balance_update`
- **Data**: `subscribe_candles`, `candle`, `subscribe_quotes`, `quote`
- **History**: `get_open_trades`, `get_trade_history`

## Documentation

- **`docs/WEBSOCKET_ARCHITECTURE.md`** - Detailed WebSocket architecture
- **`docs/WEBSOCKET_SUMMARY.md`** - Quick WebSocket overview
- **`docs/ARCHITECTURE.md`** - Overall system architecture
- **`examples/`** - Usage examples

## Testing

Mock WebSocket for testing:

```python
class MockConnection:
    async def send_request(self, msg_type, data, timeout=None):
        if msg_type == "login":
            return {"success": True, "ssid": "test"}
        elif msg_type == "place_trade":
            return {"success": True, "order_id": "test_order"}

# Use in tests
auth_service = AuthService(MockConnection())
result = await auth_service.login("test@test.com", "password")
```

## Summary

QuotexAPI's WebSocket-first architecture provides:

✅ **Real-time communication** - No polling, instant updates  
✅ **Efficient** - Single persistent connection  
✅ **Modern** - Async/await throughout  
✅ **Simple API** - Complexity hidden from users  
✅ **Event-driven** - Subscribe to what you need  
✅ **Type-safe** - Message protocol defined in code  

Perfect for a trading platform where speed and real-time data matter!

# WebSocket Architecture for QuotexAPI

## Overview

The QuotexAPI is built entirely on WebSocket communication. **All operations** - authentication, trading, data streaming, account management - happen through WebSocket messages rather than traditional REST API calls.

## Architecture Principles

### 1. WebSocket-First Design

- Single persistent WebSocket connection handles all communication
- Bidirectional: client sends requests, server sends responses and real-time events
- Message-based protocol with JSON payloads
- Request/response correlation using unique request IDs

### 2. Message Routing System

The `ConnectionService` implements sophisticated message routing:

```
┌─────────────────────────────────────────────────────────────┐
│                     ConnectionService                        │
├─────────────────────────────────────────────────────────────┤
│  • WebSocket connection management                           │
│  • Auto-reconnect with exponential backoff                   │
│  • Request/response correlation (request_id matching)        │
│  • Event subscription and routing                            │
│  • Message queue and handler registration                    │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌─────────┐      ┌─────────┐     ┌──────────┐
    │  Auth   │      │ Trading │     │   Data   │
    │ Service │      │ Service │     │ Service  │
    └─────────┘      └─────────┘     └──────────┘
```

### 3. Message Types

#### Request Messages
Sent from client to server:
- `login` - Authentication with email/password or SSID
- `logout` - End session
- `place_trade` - Place a binary options trade
- `cancel_trade` - Cancel pending trade
- `get_balance` - Request account balance
- `switch_account` - Switch between demo/real
- `subscribe_candles` - Subscribe to candle data stream
- `subscribe_quotes` - Subscribe to real-time quotes
- `get_assets` - Get available trading instruments
- `get_payout` - Get payout percentage for asset

#### Response Messages
Server responses to client requests:
- `auth_response` - Login result
- Trade placement confirmation
- Balance information
- Asset lists and payout data

#### Event Messages
Real-time events pushed by server:
- `trade_result` - Trade outcome (win/loss/draw)
- `trade_update` - Trade status changes
- `candle` - Real-time candle updates
- `quote` - Real-time price ticks
- `balance_update` - Balance changes

## Message Flow Examples

### Example 1: Authentication

```
Client                          Server
  │                               │
  ├─ login (email, password) ────►│
  │  request_id: "abc-123"        │
  │                               │
  │◄──── auth_response ───────────┤
  │      request_id: "abc-123"    │
  │      success: true            │
  │      ssid: "session_token"    │
  │      demo_balance: 10000      │
```

### Example 2: Place Trade with Live Updates

```
Client                          Server
  │                               │
  ├─ place_trade ────────────────►│
  │  request_id: "def-456"        │
  │  asset: "EURUSD"              │
  │  direction: "call"            │
  │  amount: 100                  │
  │                               │
  │◄──── trade response ──────────┤
  │      request_id: "def-456"    │
  │      order_id: "order-789"    │
  │      success: true            │
  │                               │
  │◄──── trade_update ────────────┤ (pushed event)
  │      order_id: "order-789"    │
  │      countdown: 45            │
  │                               │
  │◄──── trade_update ────────────┤ (pushed event)
  │      order_id: "order-789"    │
  │      countdown: 30            │
  │                               │
  │◄──── trade_result ────────────┤ (pushed event)
  │      order_id: "order-789"    │
  │      result: "win"            │
  │      profit: 85.00            │
```

### Example 3: Real-time Data Streaming

```
Client                          Server
  │                               │
  ├─ subscribe_candles ──────────►│
  │  asset: "EURUSD"              │
  │  timeframe: 60                │
  │                               │
  │◄──── candle ──────────────────┤ (pushed event)
  │      asset: "EURUSD"          │
  │      open: 1.0850             │
  │      high: 1.0855             │
  │      low: 1.0848              │
  │      close: 1.0852            │
  │                               │
  │◄──── candle ──────────────────┤ (next candle)
  │      asset: "EURUSD"          │
  │      ...                      │
```

## Implementation Details

### 1. Connection Service

**Key Features:**
- `send_request()` - Send message and wait for correlated response
- `send_message()` - Send fire-and-forget message
- `subscribe()` - Register event handler for message type
- `_route_message()` - Internal message dispatcher

**Request/Response Correlation:**
```python
# Each request gets unique ID
request_id = str(uuid4())
message = {
    "msg": "place_trade",
    "request_id": request_id,
    "asset": "EURUSD",
    ...
}

# Future is created to wait for response
future = asyncio.Future()
self._pending_requests[request_id] = future

# When response arrives with matching request_id
# the future is resolved with response data
await future  # Returns response
```

### 2. Service Layer

Each service (Auth, Trading, Data, Account) uses the connection service:

```python
class TradingService(BaseService):
    def __init__(self, config, connection):
        self._connection = connection
        
    async def place_trade(self, request):
        # Send request and wait for response
        response = await self._connection.send_request(
            message_type="place_trade",
            data={"asset": ..., "amount": ...},
            timeout=30.0
        )
        return parse_response(response)
```

### 3. Event Subscription

Services can subscribe to real-time events:

```python
# Subscribe to trade results
self._connection.subscribe("trade_result", self._handle_trade_update)

# Handler receives all trade_result messages
async def _handle_trade_update(self, data):
    order_id = data["order_id"]
    result = data["result"]  # "win", "loss", "draw"
    profit = data["profit"]
    # Process trade outcome
```

## Benefits of This Architecture

### 1. Real-time by Default
- No polling required
- Immediate updates for trade results, balance changes, price movements
- Lower latency

### 2. Single Connection
- Efficient resource usage
- Simplified connection management
- All services share one WebSocket

### 3. Type-safe Messages
- `ws_protocol.py` defines all message types
- Request/response structures are documented
- Easy to mock and test

### 4. Flexible Event Handling
- Subscribe to specific event types
- Multiple handlers per event
- Async or sync callbacks

### 5. Error Handling
- Timeout protection on requests
- Automatic reconnection
- Graceful disconnection

## Usage Example

```python
from QuotexAPI import QuotexAPI

async def trade_callback(update):
    print(f"Trade update: {update}")

async def main():
    api = QuotexAPI(email="user@example.com", password="password")
    
    # Connect - establishes WebSocket
    await api.connect()
    
    # Login via WebSocket message
    await api.login()
    
    # Subscribe to real-time candles
    api.subscribe_candles("EURUSD", timeframe=60)
    
    # Place trade via WebSocket
    trade = await api.place_trade(
        asset="EURUSD",
        direction="call",
        amount=100,
        expiry=60
    )
    
    # Monitor trade updates
    api.on_trade_update(trade.order_id, trade_callback)
    
    # Wait for trade to complete (receives updates via WebSocket)
    await api.wait_for_result(trade.order_id)
    
    await api.disconnect()
```

## Message Protocol Specification

### Standard Message Format

```json
{
  "msg": "message_type",
  "request_id": "unique-id",  // Optional, for request/response
  ...  // Message-specific fields
}
```

### Authentication Messages

**Login Request:**
```json
{
  "msg": "login",
  "request_id": "abc-123",
  "email": "user@example.com",
  "password": "password"
}
```

**Login Response:**
```json
{
  "msg": "auth_response",
  "request_id": "abc-123",
  "success": true,
  "ssid": "session_token",
  "user_id": "12345",
  "demo_balance": 10000.0,
  "real_balance": 0.0
}
```

### Trading Messages

**Place Trade Request:**
```json
{
  "msg": "place_trade",
  "request_id": "def-456",
  "asset": "EURUSD",
  "direction": "call",
  "amount": 100.0,
  "expiry_time": 60,
  "account_type": "demo"
}
```

**Trade Result Event:**
```json
{
  "msg": "trade_result",
  "order_id": "order-789",
  "status": "closed",
  "result": "win",
  "profit": 85.0,
  "close_price": 1.0855
}
```

### Data Streaming Messages

**Subscribe to Candles:**
```json
{
  "msg": "subscribe_candles",
  "request_id": "ghi-789",
  "asset": "EURUSD",
  "timeframe": 60
}
```

**Candle Update Event:**
```json
{
  "msg": "candle",
  "asset": "EURUSD",
  "timeframe": 60,
  "timestamp": 1732723200,
  "open": 1.0850,
  "high": 1.0855,
  "low": 1.0848,
  "close": 1.0852,
  "volume": 1250
}
```

## Testing WebSocket Communication

```python
import asyncio
from QuotexAPI.services.connection import ConnectionService
from QuotexAPI.config import QuotexConfig

async def test_websocket():
    config = QuotexConfig(ws_url="wss://example.com/ws")
    conn = ConnectionService(config)
    
    # Subscribe to events
    def on_candle(data):
        print(f"Candle: {data}")
    
    conn.subscribe("candle", on_candle)
    
    # Connect
    await conn.connect(auth_token="token")
    
    # Send request
    response = await conn.send_request(
        message_type="get_balance",
        data={}
    )
    print(f"Balance: {response}")
    
    # Keep running to receive events
    await asyncio.sleep(60)
    
    await conn.disconnect()
```

## Comparison with REST API

| Aspect | WebSocket (QuotexAPI) | Traditional REST |
|--------|----------------------|------------------|
| **Connection** | Single persistent connection | New connection per request |
| **Real-time** | Native server push | Requires polling |
| **Latency** | Lower (connection reuse) | Higher (TCP handshake) |
| **Trade Updates** | Automatic push | Must poll |
| **Data Streaming** | Built-in | Requires SSE or WebSocket anyway |
| **Complexity** | Message routing needed | Simpler request/response |
| **Resources** | 1 connection | N connections |

## Conclusion

The WebSocket-centric architecture of QuotexAPI provides:
- **Real-time communication** for trade updates and market data
- **Efficient** single connection for all operations
- **Modern** async/await patterns throughout
- **Type-safe** message protocol definitions
- **Flexible** event subscription system

This design is optimal for a trading platform where real-time data and immediate trade feedback are essential.

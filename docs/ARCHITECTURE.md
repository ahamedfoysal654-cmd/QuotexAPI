# Architecture Documentation

## Overview

QuotexAPI follows clean architecture principles with clear separation of concerns. The codebase is organized into distinct layers, each with specific responsibilities.

## Project Structure

```
QuotexAPI/
├── QuotexAPI/              # Main package
│   ├── __init__.py         # Public API exports
│   ├── client.py           # High-level API client
│   ├── config.py           # Configuration management
│   ├── enums.py            # Type-safe enumerations
│   ├── exceptions.py       # Custom exception hierarchy
│   ├── models.py           # Pydantic data models
│   ├── services/           # Service layer
│   │   ├── __init__.py
│   │   ├── base.py         # Base service class
│   │   ├── auth.py         # Authentication service
│   │   ├── connection.py   # WebSocket connection
│   │   ├── account.py      # Account management
│   │   ├── instrument.py   # Instruments/assets
│   │   ├── trading.py      # Trading operations
│   │   └── data.py         # Data and tracking
│   └── utils/              # Utilities
│       ├── __init__.py
│       └── logger.py       # Logging utilities
├── examples/               # Usage examples
├── tests/                  # Test suite
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
└── README.md              # Documentation
```

## Architecture Layers

### 1. Client Layer (`client.py`)

The `QuotexAPI` class serves as the high-level facade for all API operations. It:
- Orchestrates multiple services
- Provides a simple, intuitive interface
- Manages service lifecycle
- Handles context manager protocol

**Key Responsibilities:**
- Initialize and coordinate services
- Provide user-friendly methods
- Handle authentication flow
- Manage connections

### 2. Service Layer (`services/`)

Each service encapsulates a specific domain of functionality:

#### BaseService (`base.py`)
- Abstract base class for all services
- Handles initialization and cleanup
- Provides common service functionality

#### AuthService (`auth.py`)
- User authentication (email/password, SSID)
- Session management
- Token handling
- Logout functionality

#### ConnectionService (`connection.py`)
- WebSocket connection management
- Auto-reconnect with exponential backoff
- Connection state tracking
- Message routing

#### AccountService (`account.py`)
- Balance retrieval
- Account switching (Demo/Real)
- Account state management

#### InstrumentService (`instrument.py`)
- Asset listing and filtering
- Payout information
- Asset metadata

#### TradingService (`trading.py`)
- Trade placement
- Trade cancellation
- Trade validation

#### DataService (`data.py`)
- Open trades retrieval
- Trade history
- Trade result tracking
- Async trade monitoring

### 3. Model Layer (`models.py`)

Pydantic models provide:
- Runtime type validation
- Data serialization/deserialization
- Documentation via field descriptions
- Type safety

**Models:**
- `UserProfile` - User information
- `Balance` - Account balance data
- `Asset` - Asset/instrument details
- `Trade` - Trade information
- `TradeRequest` - Trade parameters
- `ConnectionConfig` - Connection settings

### 4. Configuration Layer (`config.py`)

- Environment variable management
- Configuration validation
- Default values
- Type-safe configuration

### 5. Exception Layer (`exceptions.py`)

Custom exception hierarchy:
```
QuotexAPIError (base)
├── AuthenticationError
│   ├── InvalidCredentialsError
│   └── SessionExpiredError
├── ConnectionError
│   ├── WebSocketError
│   └── ReconnectError
├── TradeError
│   ├── InsufficientBalanceError
│   ├── InvalidTradeParametersError
│   └── OrderNotFoundError
├── InvalidAssetError
├── TimeoutError
└── ConfigurationError
```

## Design Patterns

### 1. Service Layer Pattern
Each domain has its own service class responsible for:
- Business logic
- API communication
- State management
- Error handling

### 2. Dependency Injection
Services receive dependencies through constructor:
```python
class AuthService(BaseService):
    def __init__(self, config: QuotexConfig):
        super().__init__(config)
```

### 3. Facade Pattern
`QuotexAPI` class provides a simplified interface to complex subsystems:
```python
api = QuotexAPI(email="...", password="...")
await api.connect()
trade = await api.buy(...)  # Hides complexity
```

### 4. Strategy Pattern
Reconnection strategy can be configured:
```python
config = QuotexConfig(
    reconnect_enabled=True,
    max_reconnect_attempts=5,
    reconnect_delay=5.0
)
```

### 5. Context Manager Pattern
Automatic resource management:
```python
async with QuotexAPI(...) as api:
    # Automatic connection
    await api.buy(...)
# Automatic disconnection
```

## Data Flow

### Authentication Flow
```
Client → AuthService → API → Session Token
                              ↓
                         Store SSID
                              ↓
                    ConnectionService
```

### Trading Flow
```
Client → TradingService → Validate Parameters
                              ↓
                         Place Trade
                              ↓
                         Return Trade
                              ↓
                    DataService (tracking)
```

### WebSocket Flow
```
ConnectionService → Establish WS
                         ↓
                   Receive Messages
                         ↓
                   Route to Handler
                         ↓
                   Update State
```

## Key Design Decisions

### 1. Async/Await
- Non-blocking I/O operations
- Efficient resource usage
- Concurrent trade tracking

### 2. Type Safety
- Pydantic models for validation
- Type hints throughout
- Enum for constants

### 3. Service Separation
- Single Responsibility Principle
- Easy to test and maintain
- Clear boundaries

### 4. Configuration Management
- Environment variables
- Programmatic configuration
- Validation with Pydantic

### 5. Error Handling
- Specific exception types
- Clear error messages
- Proper error propagation

## Extension Points

### Adding New Services
1. Create service class inheriting from `BaseService`
2. Implement initialization and cleanup
3. Add to client orchestration
4. Export from `services/__init__.py`

### Adding New Endpoints
1. Add method to appropriate service
2. Define request/response models
3. Add error handling
4. Expose via client if needed

### Custom Reconnection Strategy
Subclass `ConnectionService` and override `_reconnect()`:
```python
class CustomConnectionService(ConnectionService):
    async def _reconnect(self):
        # Custom reconnection logic
        pass
```

## Testing Strategy

### Unit Tests
- Test each service independently
- Mock external dependencies
- Test error conditions

### Integration Tests
- Test service interactions
- Test full workflows
- Use mock API responses

### Example Tests
- Verify examples work
- Catch API changes
- Documentation accuracy

## Performance Considerations

### 1. Connection Pooling
- Reuse WebSocket connections
- Single session per client

### 2. Concurrent Operations
- Async for concurrent trades
- `asyncio.gather()` for bulk operations

### 3. Caching
- Cache asset information
- Cache user profile
- Invalidate on updates

### 4. Rate Limiting
- Respect API limits
- Implement backoff
- Queue requests if needed

## Security Considerations

### 1. Credential Management
- Never log credentials
- Use environment variables
- Secure session storage

### 2. Input Validation
- Validate all user inputs
- Sanitize parameters
- Type checking

### 3. Error Messages
- Don't expose sensitive data
- Generic external messages
- Detailed internal logging

## Future Improvements

1. **WebSocket Message Parsing**: Implement actual message handlers
2. **Real API Integration**: Replace mock implementations
3. **Advanced Trading**: Stop loss, take profit
4. **Signals**: Technical indicators and signals
5. **Backtesting**: Historical data testing
6. **Rate Limiting**: Automatic request throttling
7. **Caching Layer**: Redis/memory caching
8. **Metrics**: Performance monitoring
9. **Webhooks**: Event notifications
10. **Multi-account**: Manage multiple accounts

## Conclusion

The architecture is designed to be:
- **Modular**: Easy to extend and modify
- **Testable**: Clear boundaries and dependencies
- **Maintainable**: Well-organized and documented
- **Type-safe**: Extensive use of types
- **Async-first**: Non-blocking operations
- **Production-ready**: Error handling and logging

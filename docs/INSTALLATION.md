# Installation & Setup Guide

Complete guide to installing and setting up QuotexAPI.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for API communication
- **Memory**: 256 MB RAM minimum
- **Disk Space**: 50 MB

### Recommended

- **Python**: 3.10 or higher
- **Virtual Environment**: venv, virtualenv, or conda
- **Git**: For cloning the repository

## Installation Methods

### Method 1: From Source (Recommended for Development)

1. **Clone the repository**

   ```bash
   git clone https://github.com/ChipaDevTeam/QuotexAPI.git
   cd QuotexAPI
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   # Using venv (Python 3.8+)
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install the package**

   ```bash
   # Production installation
   pip install -e .
   
   # Or with development dependencies
   pip install -e ".[dev]"
   ```

### Method 2: Using Make (Unix/macOS/Linux)

```bash
git clone https://github.com/ChipaDevTeam/QuotexAPI.git
cd QuotexAPI
make install-dev
```

### Method 3: Direct Dependencies Installation

```bash
# Install only dependencies
pip install -r requirements.txt

# Or with dev dependencies
pip install -r requirements-dev.txt
```

## Configuration

### 1. Environment Variables Setup

**Create .env file:**

```bash
cp .env.example .env
```

**Edit .env file:**

```env
# Required - Authentication Credentials
QUOTEX_EMAIL=your-email@example.com
QUOTEX_PASSWORD=your-password

# Optional - SSID for session-based login
QUOTEX_SSID=your-session-id

# API Configuration (usually don't need to change)
QUOTEX_API_URL=https://api.quotex.io
QUOTEX_WS_URL=wss://ws.quotex.io

# Connection Settings
QUOTEX_RECONNECT_ENABLED=true
QUOTEX_MAX_RECONNECT_ATTEMPTS=5
QUOTEX_RECONNECT_DELAY=5

# Logging
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 2. Programmatic Configuration

You can also configure in code:

```python
from QuotexAPI import QuotexAPI, QuotexConfig

# Method 1: Direct parameters
api = QuotexAPI(
    email="user@example.com",
    password="password",
    log_level="DEBUG"
)

# Method 2: Using config object
config = QuotexConfig(
    email="user@example.com",
    password="password",
    reconnect_enabled=True,
    max_reconnect_attempts=3,
    log_level="INFO"
)
api = QuotexAPI(config=config)
```

## Verification

### 1. Verify Installation

```bash
python -c "import QuotexAPI; print(QuotexAPI.__version__)"
```

Expected output: `0.1.0`

### 2. Run Basic Test

Create `test_install.py`:

```python
import asyncio
from QuotexAPI import QuotexAPI

async def test():
    api = QuotexAPI(
        email="your-email@example.com",
        password="your-password"
    )
    
    try:
        profile = await api.connect()
        print(f"✓ Connection successful!")
        print(f"  User: {profile.email}")
        print(f"  Account: {profile.active_account}")
        
        balance = await api.get_balance()
        print(f"  Balance: ${balance.amount}")
        
        await api.disconnect()
        print("✓ Test completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")

asyncio.run(test())
```

Run:
```bash
python test_install.py
```

### 3. Run Example Scripts

```bash
# Run basic usage example
python examples/basic_usage.py

# Or using Make
make run-example
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'QuotexAPI'`

**Solutions:**
```bash
# Ensure installation
pip install -e .

# Check if package is installed
pip list | grep quotex

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Dependency Issues

**Problem:** `Import "pydantic" could not be resolved`

**Solutions:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install pydantic>=2.0.0 pydantic-settings>=2.0.0
```

### Authentication Errors

**Problem:** `AuthenticationError: Login failed`

**Solutions:**
1. Verify credentials in `.env` file
2. Ensure email and password are correct
3. Check if account is active
4. Try SSID authentication instead

```python
# Get SSID after successful login
api = QuotexAPI(email="...", password="...")
await api.connect()
ssid = api.auth.ssid
print(f"SSID: {ssid}")  # Save for future use
```

### Connection Issues

**Problem:** `ConnectionError: Failed to connect`

**Solutions:**
1. Check internet connection
2. Verify API URLs in configuration
3. Check firewall settings
4. Enable debug logging:

```python
api = QuotexAPI(
    email="...",
    password="...",
    log_level="DEBUG"
)
```

### SSL Certificate Errors

**Problem:** SSL verification failed

**Solutions:**
```bash
# Update SSL certificates
pip install --upgrade certifi

# Or use system certificates
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt  # Linux
export SSL_CERT_FILE=/etc/ssl/cert.pem  # macOS
```

### Virtual Environment Issues

**Problem:** Command not found or wrong Python version

**Solutions:**
```bash
# Ensure virtual environment is activated
# You should see (venv) in your prompt

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.8+
```

### Permission Errors

**Problem:** Permission denied during installation

**Solutions:**
```bash
# Don't use sudo with virtual environment
# Instead, create new virtual environment

# Or use --user flag (not recommended)
pip install --user -e .
```

## Development Setup

For contributors and developers:

### 1. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 2. Install Pre-commit Hooks (Optional)

```bash
pre-commit install
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=QuotexAPI --cov-report=html

# Run specific test
pytest tests/test_client.py
```

### 4. Code Quality

```bash
# Format code
black QuotexAPI/
isort QuotexAPI/

# Lint
flake8 QuotexAPI/

# Type check
mypy QuotexAPI/

# Or use Make
make format
make lint
```

## Docker Setup (Optional)

Coming soon! Docker support will be added in a future version.

## IDE Configuration

### VS Code

Create `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true
}
```

### PyCharm

1. Open project in PyCharm
2. Set Python interpreter to virtual environment
3. Mark `QuotexAPI` as sources root
4. Enable pytest as test runner

## Next Steps

After successful installation:

1. **Read Quick Start**: [docs/QUICKSTART.md](QUICKSTART.md)
2. **Explore Examples**: Check `examples/` directory
3. **Read Documentation**: Review [README.md](../README.md)
4. **Join Community**: Check GitHub Discussions

## Getting Help

- **Documentation**: See [README.md](../README.md)
- **Examples**: Check `examples/` directory
- **Issues**: [GitHub Issues](https://github.com/ChipaDevTeam/QuotexAPI/issues)
- **Architecture**: Read [docs/ARCHITECTURE.md](ARCHITECTURE.md)

## Uninstallation

To remove QuotexAPI:

```bash
# Uninstall package
pip uninstall quotex-api

# Remove virtual environment
deactivate  # If active
rm -rf venv/  # Or your venv name

# Remove repository
cd ..
rm -rf QuotexAPI/
```

---

**Need more help?** Open an issue on [GitHub](https://github.com/ChipaDevTeam/QuotexAPI/issues)

"""Pytest configuration."""

import pytest


@pytest.fixture
def mock_config():
    """Mock configuration for tests."""
    from QuotexAPI import QuotexConfig
    
    return QuotexConfig(
        email="test@example.com",
        password="password123",
        api_url="https://api.quotex.io",
        ws_url="wss://ws.quotex.io"
    )

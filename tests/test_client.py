"""Tests for QuotexAPI client."""

import pytest

from QuotexAPI import QuotexAPI, TradeDirection, AccountType


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization."""
    api = QuotexAPI(
        email="test@example.com",
        password="password123"
    )
    
    assert api.config.email == "test@example.com"
    assert api.config.password == "password123"


@pytest.mark.asyncio
async def test_connect_disconnect():
    """Test connection and disconnection."""
    api = QuotexAPI(
        email="test@example.com",
        password="password123"
    )
    
    profile = await api.connect()
    assert profile is not None
    assert api.is_connected
    
    await api.disconnect()
    assert not api.is_connected


@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager."""
    async with QuotexAPI(
        email="test@example.com",
        password="password123"
    ) as api:
        assert api.is_connected
    
    # Should be disconnected after context exit
    assert not api.is_connected


@pytest.mark.asyncio
async def test_get_balance():
    """Test getting account balance."""
    async with QuotexAPI(
        email="test@example.com",
        password="password123"
    ) as api:
        balance = await api.get_balance()
        assert balance is not None
        assert balance.amount >= 0


@pytest.mark.asyncio
async def test_get_assets():
    """Test getting available assets."""
    async with QuotexAPI(
        email="test@example.com",
        password="password123"
    ) as api:
        assets = await api.get_assets()
        assert len(assets) > 0


@pytest.mark.asyncio
async def test_place_trade():
    """Test placing a trade."""
    async with QuotexAPI(
        email="test@example.com",
        password="password123"
    ) as api:
        trade = await api.buy(
            asset="EURUSD",
            amount=10.0,
            direction=TradeDirection.CALL,
            expiry=300
        )
        
        assert trade is not None
        assert trade.order_id is not None
        assert trade.asset == "EURUSD"
        assert trade.amount == 10.0

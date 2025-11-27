"""Main QuotexAPI client."""

import logging
from datetime import datetime
from typing import List, Optional

from .config import QuotexConfig, load_config
from .enums import AccountType, AssetType, ConnectionState, TradeDirection
from .models import Asset, Balance, Trade, TradeRequest, UserProfile
from .services import (
    AccountService,
    AuthService,
    ConnectionService,
    DataService,
    InstrumentService,
    TradingService,
)
from .utils.logger import setup_logger


class QuotexAPI:
    """
    Main QuotexAPI client for interacting with Quotex broker.

    This class provides a high-level interface to all Quotex API functionality
    including authentication, trading, data retrieval, and account management.
    """

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        ssid: Optional[str] = None,
        config: Optional[QuotexConfig] = None,
        log_level: str = "INFO",
    ):
        """
        Initialize QuotexAPI client.

        Args:
            email: User email for authentication.
            password: User password for authentication.
            ssid: Session ID for SSID-based authentication.
            config: Optional configuration object. If not provided, loads from environment.
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

        Example:
            >>> api = QuotexAPI(email="user@example.com", password="password123")
            >>> await api.connect()
        """
        # Load or create configuration
        if config:
            self.config = config
        else:
            self.config = load_config()

        # Override config with provided credentials
        if email:
            self.config.email = email
        if password:
            self.config.password = password
        if ssid:
            self.config.ssid = ssid

        # Setup logging
        self.logger = setup_logger("quotex_api", log_level)

        # Initialize connection service first
        self.connection = ConnectionService(self.config)
        
        # Initialize other services with connection
        self.auth = AuthService(self.config, self.connection)
        self.account = AccountService(self.config, self.connection)
        self.instrument = InstrumentService(self.config, self.connection)
        self.trading = TradingService(self.config, self.connection)
        self.data = DataService(self.config, self.connection)

        self._initialized = False

    async def connect(self) -> UserProfile:
        """
        Connect to Quotex API and authenticate.

        This method initializes all services, authenticates the user,
        and establishes a WebSocket connection.

        Returns:
            UserProfile: Authenticated user profile.

        Raises:
            AuthenticationError: If authentication fails.
            ConnectionError: If connection fails.

        Example:
            >>> profile = await api.connect()
            >>> print(f"Connected as: {profile.email}")
        """
        self.logger.info("Connecting to Quotex API...")

        # Initialize all services
        await self.auth.initialize()
        await self.connection.initialize()
        await self.account.initialize()
        await self.instrument.initialize()
        await self.trading.initialize()
        await self.data.initialize()

        # Authenticate
        if self.config.ssid:
            profile = await self.auth.login_with_ssid(self.config.ssid)
        elif self.config.email and self.config.password:
            profile = await self.auth.login_with_email(
                self.config.email, self.config.password
            )
        else:
            raise ValueError("Either (email and password) or ssid must be provided")

        # Establish WebSocket connection
        auth_token = self.auth.ssid
        await self.connection.connect(auth_token, self._handle_ws_message)

        self._initialized = True
        self.logger.info("Successfully connected to Quotex API")

        return profile

    async def disconnect(self) -> None:
        """
        Disconnect from Quotex API and cleanup resources.

        Example:
            >>> await api.disconnect()
        """
        self.logger.info("Disconnecting from Quotex API...")

        # Cleanup all services
        await self.data.cleanup()
        await self.trading.cleanup()
        await self.instrument.cleanup()
        await self.account.cleanup()
        await self.connection.cleanup()
        await self.auth.cleanup()

        self._initialized = False
        self.logger.info("Disconnected from Quotex API")

    # Authentication Methods

    async def logout(self) -> None:
        """
        Logout from Quotex API.

        Example:
            >>> await api.logout()
        """
        await self.auth.logout()

    @property
    def is_connected(self) -> bool:
        """Check if connected to Quotex API."""
        return self.connection.is_connected

    @property
    def connection_state(self) -> ConnectionState:
        """Get current connection state."""
        return self.connection.state

    # Account & Balance Methods

    async def get_balance(self) -> Balance:
        """
        Get active account balance.

        Returns:
            Balance: Current active account balance.

        Example:
            >>> balance = await api.get_balance()
            >>> print(f"Balance: {balance.amount} {balance.currency}")
        """
        return await self.account.get_active_balance()

    async def get_all_balances(self) -> List[Balance]:
        """
        Get all account balances (Demo and Real).

        Returns:
            List[Balance]: List of all account balances.

        Example:
            >>> balances = await api.get_all_balances()
            >>> for balance in balances:
            ...     print(f"{balance.account_type}: {balance.amount}")
        """
        return await self.account.get_balances()

    async def switch_account(self, account_type: AccountType) -> Balance:
        """
        Switch between Demo and Real accounts.

        Args:
            account_type: Account type to switch to (AccountType.DEMO or AccountType.REAL).

        Returns:
            Balance: New active account balance.

        Example:
            >>> balance = await api.switch_account(AccountType.REAL)
            >>> print(f"Switched to {balance.account_type}")
        """
        return await self.account.switch_account(account_type)

    # Instrument Methods

    async def get_assets(self, asset_type: Optional[AssetType] = None) -> List[Asset]:
        """
        Get list of available binary option assets.

        Args:
            asset_type: Optional filter by asset type.

        Returns:
            List[Asset]: List of available assets.

        Example:
            >>> assets = await api.get_assets(AssetType.FOREX)
            >>> for asset in assets:
            ...     print(f"{asset.name}: {asset.current_payout}%")
        """
        return await self.instrument.get_assets(asset_type)

    async def get_payout(self, asset: str) -> float:
        """
        Get current payout percentage for a specific asset.

        Args:
            asset: Asset symbol (e.g., "EURUSD").

        Returns:
            float: Payout percentage (0-100).

        Example:
            >>> payout = await api.get_payout("EURUSD")
            >>> print(f"EUR/USD payout: {payout}%")
        """
        return await self.instrument.get_payout(asset)

    # Trading Methods

    async def buy(
        self,
        asset: str,
        amount: float,
        direction: TradeDirection,
        expiry: int,
    ) -> Trade:
        """
        Place a binary options trade.

        Args:
            asset: Asset symbol to trade (e.g., "EURUSD").
            amount: Trade amount in USD.
            direction: Trade direction (TradeDirection.CALL or TradeDirection.PUT).
            expiry: Expiry time in seconds.

        Returns:
            Trade: Placed trade information.

        Example:
            >>> trade = await api.buy(
            ...     asset="EURUSD",
            ...     amount=10.0,
            ...     direction=TradeDirection.CALL,
            ...     expiry=300
            ... )
            >>> print(f"Trade placed: {trade.order_id}")
        """
        trade_request = TradeRequest(
            asset=asset,
            amount=amount,
            direction=direction,
            expiry=expiry,
        )
        return await self.trading.place_trade(trade_request)

    async def cancel_trade(self, order_id: str) -> bool:
        """
        Cancel trade before it starts (if supported).

        Args:
            order_id: Order ID to cancel.

        Returns:
            bool: True if cancelled successfully.

        Example:
            >>> success = await api.cancel_trade("order123")
            >>> if success:
            ...     print("Trade cancelled")
        """
        return await self.trading.cancel_trade(order_id)

    # Data Methods

    async def get_open_trades(self) -> List[Trade]:
        """
        Get list of currently open trades.

        Returns:
            List[Trade]: List of open trades.

        Example:
            >>> trades = await api.get_open_trades()
            >>> for trade in trades:
            ...     print(f"{trade.asset}: {trade.direction}")
        """
        return await self.data.get_open_trades()

    async def get_trade_history(
        self,
        limit: int = 50,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Trade]:
        """
        Get trade history.

        Args:
            limit: Maximum number of trades to return.
            offset: Offset for pagination.
            start_date: Optional start date filter.
            end_date: Optional end date filter.

        Returns:
            List[Trade]: List of historical trades.

        Example:
            >>> history = await api.get_trade_history(limit=10)
            >>> for trade in history:
            ...     print(f"{trade.asset}: {trade.result} ({trade.profit})")
        """
        return await self.data.get_trade_history(
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

    async def track_trade(
        self, order_id: str, callback: Optional[callable] = None
    ) -> Trade:
        """
        Asynchronously track trade by order ID with countdown and final result.

        Args:
            order_id: Order ID to track.
            callback: Optional callback function for updates.
                      Signature: async def callback(order_id: str, remaining: float, trade: Trade)

        Returns:
            Trade: Completed trade with final result.

        Example:
            >>> async def on_update(order_id, remaining, trade):
            ...     print(f"Time remaining: {remaining}s")
            >>>
            >>> trade = await api.track_trade("order123", callback=on_update)
            >>> print(f"Final result: {trade.result}")
        """
        return await self.data.track_trade_result(order_id, callback)

    async def wait_for_result(
        self, order_id: str, timeout: Optional[float] = None
    ) -> Trade:
        """
        Blocking wait for trade result.

        Args:
            order_id: Order ID to wait for.
            timeout: Optional timeout in seconds.

        Returns:
            Trade: Completed trade with result.

        Example:
            >>> trade = await api.wait_for_result("order123", timeout=600)
            >>> print(f"Result: {trade.result}, Profit: {trade.profit}")
        """
        return await self.data.wait_for_result(order_id, timeout)

    # Private Methods

    async def _handle_ws_message(self, message: str) -> None:
        """
        Handle incoming WebSocket messages.

        Args:
            message: Raw WebSocket message.
        """
        # TODO: Implement message parsing and routing
        self.logger.debug(f"Received WebSocket message: {message}")

    # Context Manager Support

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()

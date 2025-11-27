"""Account and balance management service via WebSocket for QuotexAPI."""

import asyncio
from typing import List, Optional, Dict, Any, Callable

from ..config import QuotexConfig
from ..enums import AccountType
from ..exceptions import QuotexAPIError
from ..models import Balance
from .base import BaseService
from .connection import ConnectionService


class AccountService(BaseService):
    """Service for managing accounts and balances via WebSocket."""

    def __init__(self, config: QuotexConfig, connection: ConnectionService):
        """
        Initialize account service.

        Args:
            config: Configuration instance.
            connection: WebSocket connection service.
        """
        super().__init__(config)
        self._connection = connection
        self._balances: List[Balance] = []
        self._active_account: Optional[AccountType] = None
        self._balance_callbacks: List[Callable] = []

    async def initialize(self) -> None:
        """Initialize the account service and subscribe to balance updates."""
        await super().initialize()
        
        # Subscribe to balance update events
        self._connection.subscribe("balance_update", self._handle_balance_update)

    async def get_balances(self) -> List[Balance]:
        """
        Get all account balances (Demo and Real) via WebSocket.

        Returns:
            List[Balance]: List of balance information.

        Raises:
            QuotexAPIError: If fetching balances fails.
        """
        self._validate_initialized()
        self.logger.info("Fetching account balances")

        try:
            # Request balances via WebSocket
            response = await self._connection.send_request(
                message_type="get_balance",
                data={},
                timeout=10.0
            )
            
            if not response:
                raise QuotexAPIError("No response from server")
            
            # Parse balances
            demo_balance = response.get("demo_balance", 0.0)
            real_balance = response.get("real_balance", 0.0)
            active = response.get("active_account", "demo")
            currency = response.get("currency", "USD")
            
            self._balances = [
                Balance(
                    account_type=AccountType.DEMO,
                    amount=demo_balance,
                    currency=currency,
                    is_active=(active == "demo"),
                ),
                Balance(
                    account_type=AccountType.REAL,
                    amount=real_balance,
                    currency=currency,
                    is_active=(active == "real"),
                ),
            ]

            self._active_account = AccountType.DEMO
            self.logger.info(f"Fetched {len(self._balances)} account balances")
            return self._balances

        except Exception as e:
            self.logger.error(f"Failed to fetch balances: {str(e)}")
            raise QuotexAPIError(f"Failed to fetch balances: {str(e)}") from e

    async def get_active_balance(self) -> Balance:
        """
        Get the active account balance.

        Returns:
            Balance: Active account balance.

        Raises:
            QuotexAPIError: If no active account or fetch fails.
        """
        self._validate_initialized()

        if not self._balances:
            await self.get_balances()

        active_balance = next(
            (b for b in self._balances if b.is_active), None
        )

        if not active_balance:
            raise QuotexAPIError("No active account found")

        return active_balance

    async def switch_account(self, account_type: AccountType) -> Balance:
        """
        Switch between Demo and Real accounts via WebSocket.

        Args:
            account_type: Account type to switch to.

        Returns:
            Balance: New active account balance.

        Raises:
            QuotexAPIError: If switching fails.
        """
        self._validate_initialized()
        self.logger.info(f"Switching to {account_type.value} account")

        try:
            # Send switch account request via WebSocket
            response = await self._connection.send_request(
                message_type="switch_account",
                data={"account_type": account_type.value},
                timeout=10.0
            )
            
            if not response or not response.get("success"):
                error = response.get("error", "Switch failed") if response else "No response"
                raise QuotexAPIError(error)

            # Update active status
            for balance in self._balances:
                balance.is_active = balance.account_type == account_type

            self._active_account = account_type

            active_balance = await self.get_active_balance()
            self.logger.info(
                f"Switched to {account_type.value} account: "
                f"{active_balance.amount} {active_balance.currency}"
            )

            return active_balance

        except Exception as e:
            self.logger.error(f"Failed to switch account: {str(e)}")
            raise QuotexAPIError(f"Failed to switch account: {str(e)}") from e
    
    def on_balance_update(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register callback for balance updates.
        
        Args:
            callback: Function to call when balance updates
        """
        self._balance_callbacks.append(callback)
    
    async def _handle_balance_update(self, data: Dict[str, Any]) -> None:
        """
        Handle incoming balance update from WebSocket.
        
        Args:
            data: Balance update data
        """
        self.logger.debug(f"Balance update received: {data}")
        
        # Update cached balances
        demo_balance = data.get("demo_balance")
        real_balance = data.get("real_balance")
        active = data.get("active_account")
        
        for balance in self._balances:
            if balance.account_type == AccountType.DEMO and demo_balance is not None:
                balance.amount = demo_balance
                balance.is_active = (active == "demo")
            elif balance.account_type == AccountType.REAL and real_balance is not None:
                balance.amount = real_balance
                balance.is_active = (active == "real")
        
        # Call registered callbacks
        for callback in self._balance_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                self.logger.error(f"Balance callback error: {e}")

    @property
    def active_account_type(self) -> Optional[AccountType]:
        """Get the currently active account type."""
        return self._active_account

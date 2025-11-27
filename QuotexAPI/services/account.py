"""Account and balance management service for QuotexAPI."""

import asyncio
from typing import List, Optional

from ..config import QuotexConfig
from ..enums import AccountType
from ..exceptions import QuotexAPIError
from ..models import Balance
from .base import BaseService


class AccountService(BaseService):
    """Service for managing accounts and balances."""

    def __init__(self, config: QuotexConfig):
        """
        Initialize account service.

        Args:
            config: Configuration instance.
        """
        super().__init__(config)
        self._balances: List[Balance] = []
        self._active_account: Optional[AccountType] = None

    async def initialize(self) -> None:
        """Initialize the account service."""
        await super().initialize()

    async def get_balances(self) -> List[Balance]:
        """
        Get all account balances (Demo and Real).

        Returns:
            List[Balance]: List of balance information.

        Raises:
            QuotexAPIError: If fetching balances fails.
        """
        self._validate_initialized()
        self.logger.info("Fetching account balances")

        try:
            # TODO: Implement actual API call
            # This is a placeholder implementation
            await asyncio.sleep(0.1)  # Simulate API call

            self._balances = [
                Balance(
                    account_type=AccountType.DEMO,
                    amount=10000.0,
                    currency="USD",
                    is_active=True,
                ),
                Balance(
                    account_type=AccountType.REAL,
                    amount=0.0,
                    currency="USD",
                    is_active=False,
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
        Switch between Demo and Real accounts.

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
            # TODO: Implement actual API call
            # This is a placeholder implementation
            await asyncio.sleep(0.1)  # Simulate API call

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

    @property
    def active_account_type(self) -> Optional[AccountType]:
        """Get the currently active account type."""
        return self._active_account

"""Authentication service for QuotexAPI using WebSocket messages."""

import asyncio
from typing import Dict, Optional

from ..config import QuotexConfig
from ..exceptions import AuthenticationError, InvalidCredentialsError, SessionExpiredError
from ..models import UserProfile
from .base import BaseService
from .connection import ConnectionService


class AuthService(BaseService):
    """Authentication service using WebSocket messages for login/logout."""

    def __init__(self, config: QuotexConfig, connection: ConnectionService):
        """
        Initialize authentication service.

        Args:
            config: Configuration instance.
            connection: WebSocket connection service.
        """
        super().__init__(config)
        self._connection = connection
        self._ssid: Optional[str] = None
        self._user_profile: Optional[UserProfile] = None
        self._is_authenticated = False

    async def initialize(self) -> None:
        """Initialize the authentication service."""
        await super().initialize()

    async def cleanup(self) -> None:
        """Cleanup authentication service resources."""
        await super().cleanup()

    async def login_with_email(self, email: str, password: str) -> UserProfile:
        """
        Login with email and password via WebSocket.

        Args:
            email: User email.
            password: User password.

        Returns:
            UserProfile: User profile information.

        Raises:
            InvalidCredentialsError: If credentials are invalid.
            AuthenticationError: If authentication fails.
        """
        self._validate_initialized()
        self.logger.info(f"Attempting login with email: {email}")

        try:
            # Send login request via WebSocket
            response = await self._connection.send_request(
                message_type="login",
                data={
                    "email": email,
                    "password": password
                },
                timeout=30.0
            )
            
            # Parse response
            if not response or not response.get("success"):
                error = response.get("error", "Login failed") if response else "No response"
                raise InvalidCredentialsError(error)
            
            # Store session data
            self._ssid = response.get("ssid")
            self._user_profile = UserProfile(
                user_id=response.get("user_id", ""),
                email=email,
                username=response.get("username", email.split("@")[0]),
                demo_balance=response.get("demo_balance", 0.0),
                real_balance=response.get("real_balance", 0.0),
                active_account=response.get("active_account", "demo"),
                currency=response.get("currency", "USD"),
            )
            self._is_authenticated = True

            self.logger.info(f"Successfully logged in: {email}")
            return self._user_profile

        except InvalidCredentialsError:
            self.logger.error("Invalid credentials provided")
            raise
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            raise AuthenticationError(f"Login failed: {str(e)}") from e

    async def login_with_ssid(self, ssid: str) -> UserProfile:
        """
        Login with session ID via WebSocket.

        Args:
            ssid: Session ID.

        Returns:
            UserProfile: User profile information.

        Raises:
            SessionExpiredError: If SSID is expired or invalid.
            AuthenticationError: If authentication fails.
        """
        self._validate_initialized()
        self.logger.info("Attempting login with SSID")

        try:
            # Send SSID login request via WebSocket
            response = await self._connection.send_request(
                message_type="login",
                data={"ssid": ssid},
                timeout=30.0
            )
            
            # Parse response
            if not response or not response.get("success"):
                error = response.get("error", "SSID login failed") if response else "No response"
                raise SessionExpiredError(error)

            self._ssid = ssid
            self._user_profile = UserProfile(
                user_id=response.get("user_id", ""),
                email=response.get("email", ""),
                username=response.get("username", "user"),
                demo_balance=response.get("demo_balance", 0.0),
                real_balance=response.get("real_balance", 0.0),
                active_account=response.get("active_account", "demo"),
                currency=response.get("currency", "USD"),
            )
            self._is_authenticated = True

            self.logger.info("Successfully logged in with SSID")
            return self._user_profile

        except SessionExpiredError:
            self.logger.error("Session ID expired or invalid")
            raise
        except Exception as e:
            self.logger.error(f"SSID login failed: {str(e)}")
            raise AuthenticationError(f"SSID login failed: {str(e)}") from e

    async def logout(self) -> None:
        """
        Logout from the Quotex API via WebSocket.

        Raises:
            AuthenticationError: If logout fails.
        """
        self._validate_initialized()

        if not self._is_authenticated:
            self.logger.warning("Already logged out")
            return

        try:
            # Send logout request via WebSocket
            await self._connection.send_request(
                message_type="logout",
                data={},
                timeout=10.0
            )

            self._ssid = None
            self._user_profile = None
            self._is_authenticated = False

            self.logger.info("Successfully logged out")

        except Exception as e:
            self.logger.error(f"Logout failed: {str(e)}")
            raise AuthenticationError(f"Logout failed: {str(e)}") from e

    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self._is_authenticated

    @property
    def ssid(self) -> Optional[str]:
        """Get current session ID."""
        return self._ssid

    @property
    def user_profile(self) -> Optional[UserProfile]:
        """Get current user profile."""
        return self._user_profile

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.

        Returns:
            Dict[str, str]: Authentication headers.

        Raises:
            AuthenticationError: If not authenticated.
        """
        if not self._is_authenticated or not self._ssid:
            raise AuthenticationError("Not authenticated")

        return {
            "Authorization": f"Bearer {self._ssid}",
            "Content-Type": "application/json",
        }

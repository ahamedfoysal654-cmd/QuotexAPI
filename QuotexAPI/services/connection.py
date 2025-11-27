"""Connection management service for QuotexAPI."""

import asyncio
from typing import Callable, Optional

import websockets
from websockets.client import WebSocketClientProtocol

from ..config import QuotexConfig
from ..enums import ConnectionState
from ..exceptions import ConnectionError, ReconnectError, WebSocketError
from .base import BaseService


class ConnectionService(BaseService):
    """WebSocket connection service with auto-reconnect functionality."""

    def __init__(self, config: QuotexConfig):
        """
        Initialize connection service.

        Args:
            config: Configuration instance.
        """
        super().__init__(config)
        self._ws: Optional[WebSocketClientProtocol] = None
        self._state = ConnectionState.DISCONNECTED
        self._reconnect_attempts = 0
        self._reconnect_task: Optional[asyncio.Task] = None
        self._message_handler: Optional[Callable] = None
        self._receive_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize the connection service."""
        await super().initialize()

    async def cleanup(self) -> None:
        """Cleanup connection service resources."""
        await self.disconnect()
        await super().cleanup()

    async def connect(
        self, auth_token: str, message_handler: Optional[Callable] = None
    ) -> None:
        """
        Establish WebSocket connection.

        Args:
            auth_token: Authentication token for WebSocket connection.
            message_handler: Callback function to handle incoming messages.

        Raises:
            ConnectionError: If connection fails.
        """
        self._validate_initialized()

        if self._state == ConnectionState.CONNECTED:
            self.logger.warning("Already connected")
            return

        self._message_handler = message_handler
        self._state = ConnectionState.CONNECTING
        self.logger.info("Establishing WebSocket connection")

        try:
            # TODO: Implement actual WebSocket connection with auth
            # This is a placeholder implementation
            url = f"{self.config.ws_url}?token={auth_token}"
            self._ws = await websockets.connect(
                url, ping_interval=20, ping_timeout=10
            )

            self._state = ConnectionState.CONNECTED
            self._reconnect_attempts = 0
            self.logger.info("WebSocket connection established")

            # Start receiving messages
            if self._message_handler:
                self._receive_task = asyncio.create_task(self._receive_messages())

        except Exception as e:
            self._state = ConnectionState.FAILED
            self.logger.error(f"Connection failed: {str(e)}")
            raise ConnectionError(f"Failed to connect: {str(e)}") from e

    async def disconnect(self) -> None:
        """Disconnect from WebSocket."""
        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except asyncio.CancelledError:
                pass

        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        if self._ws:
            await self._ws.close()
            self._ws = None

        self._state = ConnectionState.DISCONNECTED
        self.logger.info("Disconnected from WebSocket")

    async def send_message(self, message: dict) -> None:
        """
        Send message through WebSocket.

        Args:
            message: Message dictionary to send.

        Raises:
            WebSocketError: If send fails.
        """
        if self._state != ConnectionState.CONNECTED or not self._ws:
            raise WebSocketError("Not connected to WebSocket")

        try:
            await self._ws.send(str(message))
            self.logger.debug(f"Sent message: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            raise WebSocketError(f"Failed to send message: {str(e)}") from e

    async def _receive_messages(self) -> None:
        """Receive and process WebSocket messages."""
        try:
            while self._ws and self._state == ConnectionState.CONNECTED:
                try:
                    message = await asyncio.wait_for(
                        self._ws.recv(), timeout=30.0
                    )

                    if self._message_handler:
                        await self._message_handler(message)

                except asyncio.TimeoutError:
                    # Timeout is normal, just continue
                    continue
                except websockets.ConnectionClosed:
                    self.logger.warning("WebSocket connection closed")
                    await self._handle_disconnect()
                    break

        except asyncio.CancelledError:
            self.logger.debug("Message receiving cancelled")
        except Exception as e:
            self.logger.error(f"Error receiving messages: {str(e)}")
            await self._handle_disconnect()

    async def _handle_disconnect(self) -> None:
        """Handle unexpected disconnection."""
        self._state = ConnectionState.DISCONNECTED

        if self.config.reconnect_enabled:
            self.logger.info("Attempting to reconnect...")
            self._reconnect_task = asyncio.create_task(self._reconnect())

    async def _reconnect(self) -> None:
        """Attempt to reconnect with exponential backoff."""
        self._state = ConnectionState.RECONNECTING

        while self._reconnect_attempts < self.config.max_reconnect_attempts:
            self._reconnect_attempts += 1
            delay = self.config.reconnect_delay * (2 ** (self._reconnect_attempts - 1))

            self.logger.info(
                f"Reconnect attempt {self._reconnect_attempts}/"
                f"{self.config.max_reconnect_attempts} in {delay}s"
            )

            await asyncio.sleep(delay)

            try:
                # TODO: Get fresh auth token and reconnect
                # This would require reference to auth service
                self.logger.info("Reconnection would happen here")
                return
            except Exception as e:
                self.logger.error(f"Reconnect attempt failed: {str(e)}")

        self._state = ConnectionState.FAILED
        self.logger.error("Max reconnection attempts reached")
        raise ReconnectError("Failed to reconnect after maximum attempts")

    @property
    def state(self) -> ConnectionState:
        """Get current connection state."""
        return self._state

    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._state == ConnectionState.CONNECTED

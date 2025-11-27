"""Connection management service for QuotexAPI with Socket.IO message routing."""

import asyncio
import json
import re
from typing import Callable, Optional, Dict, Any
from uuid import uuid4

import websockets
from websockets.client import WebSocketClientProtocol

from ..config import QuotexConfig
from ..enums import ConnectionState
from ..exceptions import ConnectionError, ReconnectError, WebSocketError
from .base import BaseService


class ConnectionService(BaseService):
    """WebSocket connection service with Socket.IO message routing."""

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
        
        # Message routing infrastructure (Socket.IO format)
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._event_handlers: Dict[str, list[Callable]] = {}
        self._request_timeout: float = 30.0
        
        # Socket.IO protocol tracking
        self._socketio_sid: Optional[str] = None

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

    def _format_socketio_message(self, event: str, data: Any) -> str:
        """
        Format message in Socket.IO format: 42["event", data]
        
        Args:
            event: Event name
            data: Event data (dict or other JSON-serializable)
            
        Returns:
            Formatted Socket.IO message string
        """
        # Socket.IO format: 42["event_name", {data}]
        payload = json.dumps([event, data])
        return f"42{payload}"
    
    def _parse_socketio_message(self, message: str) -> Optional[tuple[str, Any]]:
        """
        Parse Socket.IO format message: 42["event", data]
        
        Args:
            message: Raw message string
            
        Returns:
            Tuple of (event_name, data) or None if not parseable
        """
        # Socket.IO messages start with message type code (42 for message)
        if not message.startswith("42"):
            # Handle Socket.IO handshake messages (0, 40, etc.)
            if message.startswith("0"):
                # Handshake: 0{"sid":"...","upgrades":[],...}
                try:
                    handshake_data = json.loads(message[1:])
                    self._socketio_sid = handshake_data.get("sid")
                    self.logger.debug(f"Socket.IO handshake received, SID: {self._socketio_sid}")
                except:
                    pass
            elif message == "40":
                # Connection acknowledgment
                self.logger.debug("Socket.IO connection acknowledged")
            elif message.startswith("3"):
                # Pong response to ping
                self.logger.debug("Socket.IO pong received")
            return None
        
        try:
            # Extract the JSON array after "42"
            json_part = message[2:]
            payload = json.loads(json_part)
            
            if isinstance(payload, list) and len(payload) >= 2:
                event_name = payload[0]
                event_data = payload[1] if len(payload) > 1 else {}
                return (event_name, event_data)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse Socket.IO message: {e}")
        
        return None
    
    async def send_message(self, message: dict) -> None:
        """
        Send message through WebSocket without expecting response.

        Args:
            message: Message dictionary to send.

        Raises:
            WebSocketError: If send fails.
        """
        if self._state != ConnectionState.CONNECTED or not self._ws:
            raise WebSocketError("Not connected to WebSocket")

        try:
            await self._ws.send(json.dumps(message))
            self.logger.debug(f"Sent message: {message}")
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            raise WebSocketError(f"Failed to send message: {str(e)}") from e
    
    async def send_socketio_event(self, event: str, data: Any, expect_response: bool = False) -> Optional[Any]:
        """
        Send Socket.IO formatted event.
        
        Args:
            event: Event name (e.g., "authorization", "place_trade")
            data: Event data
            expect_response: Whether to wait for response
            
        Returns:
            Response data if expect_response is True
        """
        if self._state != ConnectionState.CONNECTED or not self._ws:
            raise WebSocketError("Not connected to WebSocket")
        
        try:
            # Format in Socket.IO format: 42["event", data]
            socketio_msg = self._format_socketio_message(event, data)
            
            self.logger.debug(f"Sending Socket.IO event '{event}': {socketio_msg}")
            await self._ws.send(socketio_msg)
            
            if expect_response:
                # Create future to wait for response
                future = asyncio.Future()
                request_id = f"{event}_{id(future)}"
                self._pending_requests[request_id] = future
                
                try:
                    response = await asyncio.wait_for(future, timeout=self._request_timeout)
                    return response
                except asyncio.TimeoutError:
                    if request_id in self._pending_requests:
                        del self._pending_requests[request_id]
                    raise WebSocketError(f"Timeout waiting for response to '{event}'")
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to send Socket.IO event: {e}")
            raise WebSocketError(f"Failed to send Socket.IO event: {str(e)}") from e
    
    async def send_request(
        self,
        message_type: str,
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        expect_response: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Send a request message and wait for correlated response.
        
        Args:
            message_type: Type of message (e.g., 'login', 'place_trade')
            data: Message payload data
            timeout: Response timeout in seconds (uses default if None)
            expect_response: Whether to wait for a response
            
        Returns:
            Response data if expect_response is True, None otherwise
            
        Raises:
            WebSocketError: If send fails or timeout occurs
        """
        if self._state != ConnectionState.CONNECTED or not self._ws:
            raise WebSocketError("Not connected to WebSocket")
        
        request_id = str(uuid4())
        message = {
            "msg": message_type,
            "request_id": request_id,
            **(data or {})
        }
        
        future = None
        if expect_response:
            future = asyncio.Future()
            self._pending_requests[request_id] = future
        
        try:
            await self._ws.send(json.dumps(message))
            self.logger.debug(f"Sent request [{request_id}]: {message_type}")
            
            if expect_response and future:
                timeout_val = timeout or self._request_timeout
                response = await asyncio.wait_for(future, timeout=timeout_val)
                return response
            
            return None
            
        except asyncio.TimeoutError:
            if request_id in self._pending_requests:
                del self._pending_requests[request_id]
            raise WebSocketError(f"Request timeout: {message_type}")
        except Exception as e:
            if request_id in self._pending_requests:
                del self._pending_requests[request_id]
            self.logger.error(f"Failed to send request: {e}")
            raise WebSocketError(f"Send failed: {str(e)}") from e
    
    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe to WebSocket events.
        
        Args:
            event_type: Type of event to listen for (e.g., 'candle', 'trade_result')
            handler: Callback function (sync or async) to handle the event
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        self.logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, handler: Callable) -> None:
        """
        Unsubscribe from WebSocket events.
        
        Args:
            event_type: Event type to unsubscribe from
            handler: Handler function to remove
        """
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                self.logger.debug(f"Unsubscribed from event: {event_type}")
            except ValueError:
                pass

    async def _receive_messages(self) -> None:
        """Receive and process WebSocket messages with Socket.IO routing."""
        try:
            while self._ws and self._state == ConnectionState.CONNECTED:
                try:
                    message = await asyncio.wait_for(
                        self._ws.recv(), timeout=30.0
                    )

                    self.logger.debug(f"Received raw message: {message}")
                    
                    # Parse Socket.IO message
                    parsed = self._parse_socketio_message(message)
                    
                    if parsed:
                        event_name, event_data = parsed
                        self.logger.debug(f"Parsed Socket.IO event '{event_name}': {event_data}")
                        
                        # Route the event
                        await self._route_socketio_event(event_name, event_data)
                        
                        # Also call legacy message handler if set
                        if self._message_handler:
                            if asyncio.iscoroutinefunction(self._message_handler):
                                await self._message_handler({"event": event_name, "data": event_data})
                            else:
                                self._message_handler({"event": event_name, "data": event_data})

                except asyncio.TimeoutError:
                    # Send Socket.IO ping to keep connection alive
                    if self._ws:
                        try:
                            await self._ws.send("2")  # Socket.IO ping
                            self.logger.debug("Sent Socket.IO ping")
                        except:
                            pass
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
    
    async def _route_socketio_event(self, event_name: str, event_data: Any) -> None:
        """
        Route Socket.IO event to appropriate handler.
        
        Args:
            event_name: Name of the event
            event_data: Event payload data
        """
        # Check if there are handlers registered for this event
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event_data)
                    else:
                        handler(event_data)
                except Exception as e:
                    self.logger.error(f"Event handler error for '{event_name}': {e}")
        
        # Also check for pending requests waiting for this event
        # (Some APIs send response as an event)
        for request_id, future in list(self._pending_requests.items()):
            if not future.done() and event_name in request_id:
                future.set_result(event_data)
                del self._pending_requests[request_id]
                break
    
    async def _route_message(self, data: Dict[str, Any]) -> None:
        """
        Route incoming message to appropriate handler.
        
        Args:
            data: Parsed message data
        """
        # Check if it's a response to a pending request
        request_id = data.get("request_id")
        if request_id and request_id in self._pending_requests:
            future = self._pending_requests.pop(request_id)
            if not future.done():
                future.set_result(data)
            return
        
        # Route to event handlers based on message type
        msg_type = data.get("msg") or data.get("type") or data.get("event")
        if msg_type and msg_type in self._event_handlers:
            for handler in self._event_handlers[msg_type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception as e:
                    self.logger.error(f"Event handler error for {msg_type}: {e}")

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

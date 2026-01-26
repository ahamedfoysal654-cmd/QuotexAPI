"""
Curl-based WebSocket transport for bypassing Cloudflare bot protection.
Uses curl_cffi library which provides curl impersonation to bypass Cloudflare.
"""

import threading
import queue
import json
import time
from typing import Optional, Dict, Callable
from curl_cffi import requests
from curl_cffi.requests import WebSocket
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CurlWebSocketTransport:
    """WebSocket transport using curl_cffi to bypass Cloudflare."""
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize curl WebSocket transport.
        
        Args:
            url: WebSocket URL (wss://...)
            headers: Optional HTTP headers
        """
        self.url = url
        self.headers = headers or {}
        self.ws: Optional[WebSocket] = None
        self.message_queue = queue.Queue()
        self.running = False
        self.reader_thread: Optional[threading.Thread] = None
        self._on_message: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._on_close: Optional[Callable] = None
        
    def connect(self) -> bool:
        """
        Connect to WebSocket via curl_cffi.
        
        Returns:
            True if connection successful, False otherwise
        """
        logger.info("Starting curl_cffi WebSocket connection...")
        logger.debug(f"URL: {self.url}")
        
        try:
            # Create session with browser impersonation
            session = requests.Session(impersonate="chrome110")
            
            # Prepare headers
            headers = {
                'Origin': 'https://qxbroker.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                **self.headers
            }
            
            # Connect to WebSocket
            self.ws = session.ws_connect(self.url, headers=headers)
            
            self.running = True
            
            # Start reader thread
            self.reader_thread = threading.Thread(
                target=self._read_messages,
                daemon=True,
                name="CurlWebSocketReader"
            )
            self.reader_thread.start()
            
            logger.info("Curl WebSocket connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            if self._on_error:
                self._on_error(e)
            return False
    
    def _read_messages(self):
        """Read messages from curl stdout in background thread."""
        buffer = ""
        
        while self.running and self.process and self.process.poll() is None:
            try:
                # Read one character at a time
                char = self.process.stdout.read(1)
                if not char:
                    time.sleep(0.01)
                    continue
                    WebSocket in background thread."""
        while self.running and self.ws:
            try:
                # Receive message from WebSocket
                message = self.ws.recv()
                if not message:
                    time.sleep(0.01)
                    continue
                
                # Handle binary or text messages
                if isinstance(message, bytes):
                    message = message.decode('utf-8')
                
                # Put message in queue
                self.message_queue.put(message)
                
                # Call callback if set
                if self._on_message:
                    try:
                        self._on_message(message)
                    except Exception as e:
                        logger.error(f"Error in message callback: {e}")
            self._on_close()
    
    def send(self, message: str) -> bool:
        """
        Send message through curl stdin.
        
        Args:
            message: Message string to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.process or not self.process.stdin:
            logger.error("Cannot send: not connected")
            return False
            
        try:
            self.process.stdin.write(message)
            if not message.endswith('\n'):
                self.process.stdin.write('\n')
            self.process.stdin.flush()
            logger.debug(f"Sent: {message[:100]}...")
            return True
        except Exception as e:
            logger.error(f"Send error: {e}")
            if self._on_error:
                self._on_error(e)
            return False
    
    def recv(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Receive message from queue (blocking).
        
        Args:
            timeout: Timeout in seconds (None = block forever)
            
        Returns:WebSocket.
        
        Args:
            message: Message string to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.ws:
            logger.error("Cannot send: not connected")
            return False
            
        try:
            self.ws.send(messageCallable[[], None]):
        """Set callback for connection close."""
        self._on_close = callback
    
    def close(self):
        """Close the WebSocket connection."""
        self.running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()
            
            self.process = None
        
        logger.info("Curl WebSocket connection closed")
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return (
            self.running and
            self.process is not None and
            self.process.poll() is None
        )
ws:ws is not
                self.ws.close()
            except:
                pass
            
            self.w
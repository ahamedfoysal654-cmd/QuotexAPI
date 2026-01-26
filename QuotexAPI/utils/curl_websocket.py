"""
Curl-based WebSocket transport for bypassing Cloudflare bot protection.
Uses curl subprocess as transport layer since it bypasses Cloudflare successfully.
"""

import subprocess
import threading
import queue
import json
import time
from typing import Optional, Dict, Callable
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CurlWebSocketTransport:
    """WebSocket transport using curl subprocess to bypass Cloudflare."""
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize curl WebSocket transport.
        
        Args:
            url: WebSocket URL (wss://...)
            headers: Optional HTTP headers
        """
        self.url = url
        self.headers = headers or {}
        self.process: Optional[subprocess.Popen] = None
        self.message_queue = queue.Queue()
        self.running = False
        self.reader_thread: Optional[threading.Thread] = None
        self._on_message: Optional[Callable] = None
        self._on_error: Optional[Callable] = None
        self._on_close: Optional[Callable] = None
        
    def connect(self) -> bool:
        """
        Connect to WebSocket via curl.
        
        Returns:
            True if connection successful, False otherwise
        """
        cmd = ['curl', self.url]
        
        # Add custom headers
        for key, value in self.headers.items():
            cmd.extend(['-H', f'{key}: {value}'])
        
        # Essential WebSocket headers
        cmd.extend([
            '-H', 'Upgrade: websocket',
            '-H', 'Connection: Upgrade',
            '-H', 'Sec-WebSocket-Version: 13',
            '-H', 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==',
            '-H', 'Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits',
            '--no-buffer'  # Disable buffering for real-time communication
        ])
        
        logger.info("Starting curl WebSocket connection...")
        logger.debug(f"URL: {self.url}")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0  # Unbuffered
            )
            
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
            logger.error(f"Failed to start curl: {e}")
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
                    
                buffer += char
                
                # Detect complete Socket.IO messages
                message_detected = False
                
                # Handshake: 0{...}
                if buffer.startswith('0{'):
                    if buffer.count('{') == buffer.count('}') and buffer.count('{') > 0:
                        message_detected = True
                        
                # Namespace connect/disconnect: 40, 41
                elif buffer in ['40', '41']:
                    message_detected = True
                    
                # Ping/Pong: 2, 3
                elif buffer in ['2', '3']:
                    message_detected = True
                    
                # Event message: 42[...]
                elif buffer.startswith('42['):
                    if buffer.count('[') == buffer.count(']') and buffer.count('[') > 0:
                        message_detected = True
                        
                # Acknowledgment: 451-[...], 450-[...]
                elif buffer.startswith('45') and '-' in buffer:
                    dash_idx = buffer.index('-')
                    json_part = buffer[dash_idx + 1:]
                    if json_part and json_part.startswith('['):
                        if json_part.count('[') == json_part.count(']'):
                            message_detected = True
                
                if message_detected:
                    # Put message in queue
                    self.message_queue.put(buffer)
                    
                    # Call callback if set
                    if self._on_message:
                        try:
                            self._on_message(buffer)
                        except Exception as e:
                            logger.error(f"Error in message callback: {e}")
                    
                    buffer = ""
                    
            except Exception as e:
                if self.running:
                    logger.error(f"Read error: {e}")
                    if self._on_error:
                        self._on_error(e)
                break
        
        # Connection closed
        if self._on_close:
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
            
        Returns:
            Message string or None if timeout
        """
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def set_on_message(self, callback: Callable[[str], None]):
        """Set callback for incoming messages."""
        self._on_message = callback
    
    def set_on_error(self, callback: Callable[[Exception], None]):
        """Set callback for errors."""
        self._on_error = callback
    
    def set_on_close(self, callback: Callable[[], None]):
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

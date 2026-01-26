"""
Curl-based WebSocket transport for bypassing Cloudflare bot protection.
Uses curl subprocess as transport layer since it bypasses Cloudflare successfully.

Note: This uses curl with --http1.1 upgrade to establish WebSocket connection.
For bidirectional communication, we write to stdin and read from stdout.
"""

import subprocess
import threading
import queue
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
        cmd = ['curl', '-N', '--http1.1', self.url]
        
        # Add custom headers
        for key, value in self.headers.items():
            cmd.extend(['-H', f'{key}: {value}'])
        
        # Essential WebSocket headers matching the working command
        cmd.extend([
            '-H', 'Upgrade: websocket',
            '-H', 'Connection: Upgrade',
            '-H', 'Sec-WebSocket-Version: 13',
            '-H', 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==',
            '-H', 'Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits',
            '-H', 'Origin: https://qxbroker.com',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/126.0.0.0',
            '-H', 'Cache-Control: no-cache',
            '-H', 'Pragma: no-cache',
            '-H', 'Accept-Language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            '--no-buffer'
        ])
        
        logger.info("Starting curl WebSocket connection...")
        logger.debug(f"URL: {self.url}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
            self.running = True
            
            # Start reader thread
            self.reader_thread = threading.Thread(
                target=self._read_messages,
                daemon=True,
                name="CurlWebSocketReader"
            )
            self.reader_thread.start()
            
            # Wait a bit to see if connection succeeds
            time.sleep(0.5)
            
            if self.process.poll() is not None:
                # Process died
                stderr = self.process.stderr.read().decode('utf-8', errors='ignore')
                logger.error(f"Curl process died: {stderr}")
                return False
            
            logger.info("Curl WebSocket connection established")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start curl: {e}")
            if self._on_error:
                self._on_error(e)
            return False
    
    def _read_messages(self):
        """Read messages from curl stdout in background thread."""
        buffer = b""
        
        while self.running and self.process and self.process.poll() is None:
            try:
                # Read raw bytes
                chunk = self.process.stdout.read(1)
                if not chunk:
                    time.sleep(0.01)
                    continue
                    
                buffer += chunk
                
                # Try to decode and detect complete Socket.IO messages
                try:
                    text = buffer.decode('utf-8')
                except UnicodeDecodeError:
                    # Need more bytes
                    continue
                
                message_detected = False
                
                # Handshake: 0{...}
                if text.startswith('0{'):
                    if text.count('{') == text.count('}') and text.count('{') > 0:
                        message_detected = True
                        
                # Namespace connect/disconnect: 40, 41
                elif text in ['40', '41']:
                    message_detected = True
                    
                # Ping/Pong: 2, 3
                elif text in ['2', '3']:
                    message_detected = True
                    
                # Event message: 42[...]
                elif text.startswith('42['):
                    if text.count('[') == text.count(']') and text.count('[') > 0:
                        message_detected = True
                        
                # Acknowledgment: 451-[...], 450-[...]
                elif text.startswith('45') and '-' in text:
                    dash_idx = text.index('-')
                    json_part = text[dash_idx + 1:]
                    if json_part and json_part.startswith('['):
                        if json_part.count('[') == json_part.count(']'):
                            message_detected = True
                
                if message_detected:
                    # Put message in queue
                    self.message_queue.put(text)
                    
                    # Call callback if set
                    if self._on_message:
                        try:
                            self._on_message(text)
                        except Exception as e:
                            logger.error(f"Error in message callback: {e}")
                    
                    buffer = b""
                    
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
        Send message through WebSocket.
        
        For WebSocket frames, we need to wrap the message properly.
        Since curl handles the WebSocket protocol, we send the raw frame.
        
        Args:
            message: Message string to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.process or not self.process.stdin:
            logger.error("Cannot send: not connected")
            return False
            
        try:
            # Encode message as bytes
            msg_bytes = message.encode('utf-8')
            
            # Create WebSocket text frame (FIN=1, opcode=1 for text)
            # Simple WebSocket frame: FIN(1) + RSV(000) + OPCODE(0001) = 0x81
            # Then mask bit (1) + payload length
            frame = bytearray()
            frame.append(0x81)  # FIN + text frame
            
            payload_len = len(msg_bytes)
            if payload_len < 126:
                frame.append(0x80 | payload_len)  # Mask bit + length
            elif payload_len < 65536:
                frame.append(0x80 | 126)
                frame.extend(payload_len.to_bytes(2, 'big'))
            else:
                frame.append(0x80 | 127)
                frame.extend(payload_len.to_bytes(8, 'big'))
            
            # Masking key (required for client-to-server frames)
            import os
            mask = os.urandom(4)
            frame.extend(mask)
            
            # Masked payload
            for i, byte in enumerate(msg_bytes):
                frame.append(byte ^ mask[i % 4])
            
            # Write to stdin
            self.process.stdin.write(frame)
            self.process.stdin.flush()
            
            logger.debug(f"Sent WebSocket frame ({len(frame)} bytes): {message[:100]}...")
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
                # Send close frame (0x88)
                if self.process.stdin:
                    try:
                        frame = bytearray([0x88, 0x00])  # Close frame, no payload
                        self.process.stdin.write(frame)
                        self.process.stdin.flush()
                    except:
                        pass
                
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

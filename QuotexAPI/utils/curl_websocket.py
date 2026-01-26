"""
Curl-based WebSocket transport for bypassing Cloudflare bot protection.
Uses curl subprocess for RECEIVING (WebSocket) and curl_cffi for SENDING (HTTP polling).

This hybrid approach works because:
- Curl subprocess can receive WebSocket messages (bypasses Cloudflare)
- Curl_cffi can send via HTTP POST to Socket.IO polling endpoint (bypasses Cloudflare)
- Socket.IO supports mixed transports (receive via WS, send via polling)
"""

import subprocess
import threading
import queue
import time
from typing import Optional, Dict, Callable
from curl_cffi import requests
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CurlWebSocketTransport:
    """Hybrid WebSocket transport: curl subprocess for receiving, curl_cffi HTTP for sending."""
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize hybrid transport.
        
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
        
        # For HTTP polling (sending)
        self.session = None
        self.sid = None  # Socket.IO session ID
        self.polling_url = None
        
    def connect(self) -> bool:
        """
        Connect to WebSocket via curl.
        First establishes HTTP polling session to get valid SID for sending.
        
        Returns:
            True if connection successful, False otherwise
        """
        # Step 1: Establish HTTP polling session first to get valid SID
        print("[HYBRID] Step 1: Establishing HTTP polling session...")
        try:
            base_url = self.url.replace('wss://', 'https://').replace('transport=websocket', 'transport=polling')
            
            self.session = requests.Session(impersonate="chrome110")
            headers = {
                'Origin': 'https://qxbroker.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                **self.headers
            }
            
            response = self.session.get(base_url, headers=headers, timeout=10)
            print(f"[HYBRID] Polling handshake response: {response.text[:200]}")
            
            if response.status_code == 200 and response.text.startswith('0{'):
                import json
                handshake = json.loads(response.text[1:])
                self.sid = handshake.get('sid')
                self.polling_url = base_url
                print(f"[HYBRID] Got SID from polling: {self.sid}")
                
                # Step 1b: Send namespace connect via polling
                print("[HYBRID] Sending namespace connect via polling...")
                url_with_sid = f"{self.polling_url}&sid={self.sid}"
                response = self.session.post(url_with_sid, headers=headers, data='40', timeout=10)
                print(f"[HYBRID] Namespace connect response: {response.text[:100]}")
            else:
                logger.error(f"Failed to establish polling session: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to establish polling session: {e}")
            print(f"[HYBRID] Error establishing polling: {e}")
            return False
        
        # Step 2: Now start curl WebSocket for receiving
        print("[HYBRID] Step 2: Starting curl WebSocket for receiving...")
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
            
            # Start reader threads
            self.reader_thread = threading.Thread(
                target=self._read_messages,
                daemon=True,
                name="CurlWebSocketReader"
            )
            self.reader_thread.start()
            
            # Start stderr reader
            self.stderr_thread = threading.Thread(
                target=self._read_stderr,
                daemon=True,
                name="CurlStderrReader"
            )
            self.stderr_thread.start()
            
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
    
    def _extract_sid_from_handshake(self, message: str) -> Optional[str]:
        """Extract Socket.IO session ID from handshake message."""
        try:
            if message.startswith('0{'):
                import json
                handshake = json.loads(message[1:])
                return handshake.get('sid')
        except:
            pass
        return None
    
    def _read_messages(self):
        """Read messages from curl stdout in background thread."""
        buffer = b""
        
        print("[CURL READER] Starting message reader thread")
        
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
                        # Extract SID for HTTP polling
                        if not self.sid:
                            self.sid = self._extract_sid_from_handshake(text)
                            if self.sid:
                                # Setup HTTP polling URL
                                base_url = self.url.replace('wss://', 'https://').replace('/socket.io/?', '/socket.io/?')
                                if '?' in base_url:
                                    self.polling_url = base_url.replace('transport=websocket', 'transport=polling')
                                else:
                                    self.polling_url = base_url + '?EIO=3&transport=polling'
                                print(f"[CURL READER] Extracted SID: {self.sid}, polling URL: {self.polling_url}")
                                
                                # Create curl_cffi session for sending
                                self.session = requests.Session(impersonate="chrome110")
                        
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
                    print(f"[CURL READER] Complete message received: {text[:200]}...")
                    
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
                    print(f"[CURL READER] Error: {e}")
                    if self._on_error:
                        self._on_error(e)
                break
        
        print("[CURL READER] Reader thread exiting")
        
        # Connection closed
        if self._on_close:
            self._on_close()
    
    def _read_stderr(self):
        """Read stderr from curl to catch any errors."""
        print("[CURL STDERR] Starting stderr reader")
        while self.running and self.process:
            try:
                line = self.process.stderr.readline()
                if line:
                    error_msg = line.decode('utf-8', errors='ignore').strip()
                    if error_msg:
                        print(f"[CURL STDERR] {error_msg}")
                        logger.warning(f"Curl stderr: {error_msg}")
                else:
                    time.sleep(0.1)
            except Exception as e:
                if self.running:
                    print(f"[CURL STDERR] Error reading: {e}")
                break
        print("[CURL STDERR] Stderr reader exiting")
    
    def send(self, message: str) -> bool:
        """
        Send message via HTTP polling (using curl_cffi).
        
        Args:
            message: Socket.IO message string to send (e.g., "42[...]")
            
        Returns:
            True if sent successfully, False otherwise
        """
        print(f"[HTTP SEND] Attempting to send via HTTP polling: {message[:100]}...")
        
        if not self.session or not self.sid or not self.polling_url:
            print("[HTTP SEND] ERROR: Not ready (no session/sid/url)")
            logger.error("Cannot send: HTTP polling not initialized")
            return False
            
        try:
            # Add sid to URL
            url_with_sid = f"{self.polling_url}&sid={self.sid}"
            
            # Prepare headers
            headers = {
                'Origin': 'https://qxbroker.com',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'text/plain;charset=UTF-8',
                'Accept': '*/*',
                **self.headers
            }
            
            print(f"[HTTP SEND] POST to {url_with_sid[:100]}...")
            print(f"[HTTP SEND] Data: {message}")
            
            # Send via HTTP POST
            response = self.session.post(
                url_with_sid,
                headers=headers,
                data=message,
                timeout=10
            )
            
            print(f"[HTTP SEND] Response status: {response.status_code}")
            print(f"[HTTP SEND] Response: {response.text[:200]}")
            
            if response.status_code == 200:
                logger.debug(f"Sent via HTTP polling: {message[:100]}...")
                return True
            else:
                logger.error(f"HTTP send failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"[HTTP SEND] ERROR: {e}")
            logger.error(f"HTTP send error: {e}")
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

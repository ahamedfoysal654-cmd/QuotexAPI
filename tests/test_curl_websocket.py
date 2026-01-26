"""
WebSocket client using subprocess curl (bypasses Cloudflare)
Since curl works but Python WebSocket libraries are blocked by Cloudflare,
we'll use curl as the transport layer.
"""

import subprocess
import threading
import queue
import json
import time
import sys

class CurlWebSocket:
    """WebSocket client that uses curl as transport."""
    
    def __init__(self, url, headers=None):
        """Initialize curl WebSocket client."""
        self.url = url
        self.headers = headers or {}
        self.process = None
        self.message_queue = queue.Queue()
        self.running = False
        self.reader_thread = None
        
    def connect(self):
        """Connect to WebSocket via curl."""
        cmd = ['curl', self.url]
        
        # Add headers
        for key, value in self.headers.items():
            cmd.extend(['-H', f'{key}: {value}'])
        
        # Essential WebSocket headers
        cmd.extend([
            '-H', 'Upgrade: websocket',
            '-H', 'Connection: Upgrade',
            '-H', 'Sec-WebSocket-Version: 13',
            '-H', 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==',
            '-H', 'Sec-WebSocket-Extensions: permessage-deflate; client_max_window_bits',
            '--no-buffer'  # Important: disable buffering
        ])
        
        print(f"🔌 Starting curl process...")
        print(f"   Command: {' '.join(cmd[:3])}...")
        
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
            self.reader_thread = threading.Thread(target=self._read_messages, daemon=True)
            self.reader_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start curl: {e}")
            return False
    
    def _read_messages(self):
        """Read messages from curl stdout."""
        buffer = ""
        while self.running and self.process and self.process.poll() is None:
            try:
                # Read character by character
                char = self.process.stdout.read(1)
                if not char:
                    time.sleep(0.01)
                    continue
                    
                buffer += char
                
                # Detect complete Socket.IO messages
                # Messages are typically not newline-delimited but come one after another
                message_detected = False
                
                # Handshake: 0{...}
                if buffer.startswith('0{') and buffer.count('{') == buffer.count('}') and buffer.count('{') > 0:
                    message_detected = True
                # Namespace: 40, 41
                elif buffer in ['40', '41']:
                    message_detected = True
                # Ping/Pong: 2, 3
                elif buffer in ['2', '3']:
                    message_detected = True
                # Event: 42[...]
                elif buffer.startswith('42['):
                    # Count brackets to detect complete JSON
                    if buffer.count('[') == buffer.count(']') and buffer.count('[') > 0:
                        message_detected = True
                # Ack: 451-[...]  or 450-[...]
                elif buffer.startswith('45') and '-' in buffer:
                    # Check if we have complete JSON after the dash
                    dash_idx = buffer.index('-')
                    json_part = buffer[dash_idx+1:]
                    if json_part:
                        try:
                            # Try to count brackets
                            if json_part.startswith('[') and json_part.count('[') == json_part.count(']'):
                                message_detected = True
                        except:
                            pass
                
                if message_detected:
                    self.message_queue.put(buffer)
                    buffer = ""
                    
            except Exception as e:
                if self.running:
                    print(f"⚠️  Read error: {e}")
                break
    
    def send(self, message):
        """Send message via curl stdin."""
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(message)
                if not message.endswith('\n'):
                    self.process.stdin.write('\n')
                self.process.stdin.flush()
                return True
            except Exception as e:
                print(f"❌ Send error: {e}")
                return False
        return False
    
    def receive(self, timeout=None):
        """Receive message from queue."""
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def close(self):
        """Close connection."""
        self.running = False
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()


def main():
    """Test curl WebSocket connection."""
    print("=" * 60)
    print("Quotex WebSocket via CURL")
    print("=" * 60)
    
    # Get SSID
    ssid_input = input("\n🔑 Enter SSID or full auth message: ").strip()
    
    # Extract auth data
    auth_data = None
    if ssid_input.startswith('42["authorization"'):
        import re
        match = re.search(r'42\["authorization",(\{.+\})\]', ssid_input)
        if match:
            auth_data = json.loads(match.group(1))
            auth_msg = ssid_input
            print(f"📝 Using full auth with isDemo={auth_data.get('isDemo')}, tournamentId={auth_data.get('tournamentId')}")
    else:
        auth_data = {"session": ssid_input}
        auth_msg = f'42["authorization",{json.dumps(auth_data)}]'
        print(f"📝 Using session: {ssid_input[:20]}...")
    
    url = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 OPR/126.0.0.0",
        "Origin": "https://qxbroker.com",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    ws = CurlWebSocket(url, headers)
    
    if ws.connect():
        print("✅ Connected!")
        
        try:
            # Receive handshake and initial messages
            start_time = time.time()
            authorized = False
            message_count = 0
            
            while time.time() - start_time < 0.5)
                
                if message:
                    message_count += 1
                    print(f"\n📥 [{message_count}] {message[:150]
                    print(f"\n📥 {message}")
                    
                    if message.startswith('0{'):
                        # Handshake
                        data = json.loads(message[1:])
                        print(f"   🔧 SID: {data.get('sid')}")
                        
                    elif message.startswith('40') and not authorized:
                        # Namespace connected - send auth
                        print(f"\n📤 Sending: {auth_msg[:80]}...")
                        ws.send(auth_msg)
                        authorized = True
                        
                        # Request data
                        time.sleep(0.5)
                        balance_req = '42["s_balance/list",{"_placeholder":true,"num":0}]'
                        print(f"📤 Sending: {balance_req}")
                        ws.send(balance_req)
                        
                        time.sleep(0.5)
                        inst_req = '42["instruments/list",{"_placeholder":true,"num":0}]'
                        print(f"📤 Sending: {inst_req}")
                        ws.send(inst_req)
                        
                    elif message == '2':
                        # Ping
                        print("💓 Ping - sending pong")
                        ws.send('3')
                        
                    elif message.startswith('42'):
                        # Event
                        try:
                            data = json.loads(message[2:])
                            event = data[0] if data else "unknown"
                            print(f"   📨 Event: {event}")
                            if len(data) > 1:
                                print(f"   Data: {str(data[1])[:200]}")
                        except:
                            print(f"   Data: {message[2:][:200]}")
                            
                    elif message.startswith('451'):
                        print(f"   ✔️  ACK")
                        try:
                            # Parse ack data
                            data = message.split('-', 1)[1] if '-' in message else ""
                            if data:
                                parsed = json.loads(data)
                                print(f"   Response: {str(parsed)[:300]}")
                        except:
                            print(f"   Response: {message[:200]}")
                
                # Check if process is still running
                if ws.process and ws.process.poll() is not None:
                    print
            
            print(f"\n📊 Total messages received: {message_count}")("\n⚠️  Curl process terminated")
                    break
                    
        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user")
        finally:
            ws.close()
    else:
        print("❌ Failed to connect")
    
    print("\n✅ Done")


if __name__ == "__main__":
    main()

import socket
import time
import json
import threading
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("XilicaDriver")

class XilicaDriver:
    def __init__(self, ip, port=10025, protocol='TCP'):
        self.ip = ip
        self.port = port
        self.protocol = protocol.upper()
        self.sock = None
        self.is_connected = False
        self.running = False
        
        # Knowledge Base (Protocol Dictionary)
        # Format: {'ACTION_NAME': {'cmd': 'command_string', 'type': 'string/hex'}}
        self.protocol_map = {} 
        
    def load_protocol(self, filepath="config_learned.json"):
        """Loads a learned protocol configuration from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                self.protocol_map = json.load(f)
            logger.info(f"Loaded protocol map with {len(self.protocol_map)} commands.")
        except FileNotFoundError:
            logger.warning("No protocol file found. Starting with empty knowledge.")

    def save_protocol(self, filepath="config_learned.json"):
        """Saves the current learned protocol to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.protocol_map, f, indent=4)
        logger.info(f"Saved protocol map to {filepath}.")

    def connect(self):
        """Establishes the network connection."""
        try:
            if self.sock:
                self.sock.close()

            if self.protocol == 'TCP':
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(5)
                self.sock.connect((self.ip, self.port))
                self.is_connected = True
                logger.info(f"✅ Connected to Xilica at {self.ip}:{self.port} (TCP)")
            
            elif self.protocol == 'UDP':
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.settimeout(5)
                # UDP doesn't "connect" but we bind to send/recv
                self.is_connected = True
                logger.info(f"✅ UDP Socket ready for {self.ip}:{self.port}")

        except Exception as e:
            self.is_connected = False
            logger.error(f"❌ Connection Failed: {e}")
            return False
        return True

    def send_raw(self, data):
        """Sends raw data (bytes or string)."""
        if not self.is_connected:
            if not self.connect():
                return False
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8') # Default to UTF-8
            
            if self.protocol == 'TCP':
                self.sock.sendall(data)
            else:
                self.sock.sendto(data, (self.ip, self.port))
            
            logger.debug(f"📤 SENT: {data}")
            return True
        except Exception as e:
            logger.error(f"Failed to send: {e}")
            self.is_connected = False
            return False

    def send_command(self, action_name):
        """Sends a command by its logical name (e.g., 'MUTE_CH1')."""
        if action_name not in self.protocol_map:
            logger.error(f"Unknown action: {action_name}")
            return False
        
        cmd_info = self.protocol_map[action_name]
        cmd_str = cmd_info['cmd']
        
        # Auto-detect Hex vs String
        if cmd_info.get('type') == 'hex':
            data = bytes.fromhex(cmd_str)
        else:
            data = cmd_str # Assumes string
            
        logger.info(f"Executed logical command: {action_name}")
        return self.send_raw(data)

    def listen_raw(self, timeout=10):
        """Listens for raw response for a set duration (blocking)."""
        if not self.is_connected:
            self.connect()
            
        try:
            self.sock.settimeout(timeout)
            if self.protocol == 'TCP':
                data = self.sock.recv(1024)
            else:
                data, addr = self.sock.recvfrom(1024)
            
            logger.info(f"📥 RECEIVED: {data}")
            return data
        except socket.timeout:
            logger.warning("Wait timed out. No data received.")
            return None
        except Exception as e:
            logger.error(f"Receive error: {e}")
            return None

    def close(self):
        if self.sock:
            self.sock.close()
        self.is_connected = False
        logger.info("Connection closed.")

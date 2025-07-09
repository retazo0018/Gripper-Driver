# driver_client.py

import socket
import time
import threading


class GripperState:
    """Represents the internal state of the gripper."""
    def __init__(self):
        self.width_mm = 0.0
        self.speed = 0.0
        self.torque = 0.0
        self.is_calibrated = False
        self.min_width = 0.0
        self.max_width = 0.0  # default max


class GripperDriver:
    def __init__(self, host='127.0.0.1', port=8000, timeout=2):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.state = GripperState()
        self.lock = threading.Lock()
        self.connected = False
        self._connect()

    def _connect(self):
        """Establish TCP connection to gripper."""
        try:
            print(f"[INFO] Connecting to gripper at {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print("[INFO] Connection established.")
            self.get_status()
            
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            self.connected = False
            print(f"[ERROR] Connection failed: {e}")
            self._attempt_recovery()     

    def _send_command(self, cmd):
        """Send a string command over TCP."""
        if not self.connected:
            self._attempt_recovery()
        try:
            self.socket.sendall(cmd.encode('utf-8'))
            print(f"[COMMAND] Sent: {cmd}")
        except (BrokenPipeError, OSError):
            print("[ERROR] Lost connection while sending.")
            self.connected = False
            self._attempt_recovery()

    def _receive_response(self):
        """Receive and parse response from the gripper."""
        try:
            data = self.socket.recv(1024).decode('utf-8')
            print(f"[RESPONSE] Received: {data}")
            return data
        except socket.timeout:
            print("[WARNING] Response timeout.")
            return None
    
    def _attempt_recovery(self):
        """Attempt to reconnect to the gripper."""
        print("[INFO] Attempting communication recovery...")
        time.sleep(1)
        try:
            if self.socket:
                self.socket.close()
        except:
            pass
        self._connect()

    def move_to(self, width_mm):
        """Command the gripper to move to a specified width."""
        with self.lock:
            if not self.state.is_calibrated:
                print("[WARNING] Gripper not calibrated. Calibrating...")
                self.calibrate()
                self.state.is_calibrated = True
            if not (self.state.min_width <= width_mm <= self.state.max_width):
                print("[ERROR] Width out of range.")
                return
            self._send_command(f"MOVE {width_mm}")
            ack = self._receive_response()
            print(f"[CLIENT] Server responded: {ack}")

    def get_status(self):
        self._send_command("STATUS")
        print("[CLIENT] Sent STATUS command")
        response = self._receive_response()
        self.state.width_mm, self.state.speed, self.state.torque, self.state.min_width, self.state.max_width = map(float, response.strip().split(","))
        return response

    def calibrate(self):
        self._send_command("CALIBRATE")
        print("[CLIENT] Sent CALIBRATE command")
        response = self._receive_response()
        return response
    
    def execute_sequence(self, sequence):
        for action in sequence:
            cmd, val = action
            if cmd == "MOVE":
                self.move_to(val)
            elif cmd == "WAIT":
                time.sleep(val)


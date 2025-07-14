# driver_client.py

import socket
import time
import threading
from datetime import datetime
import re
from interact import run_cli_ui

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
    def __init__(self, host='127.0.0.1', port=8000, timeout=5):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.state = GripperState()
        self.lock = threading.Lock()
        self.connected = False
        self.multi_part_commands = ["MOVE", "CALIBRATE"]
        self._connect()

    def _connect(self):
        """Establish TCP connection to gripper."""
        try:
            print(f"[INFO] Connecting to gripper at {self.host}:{self.port}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            print("[E_SUCCESS] Connection established.")
            self.connected = True
            self._initialize_gripperstate()
            if not self.state.is_calibrated:
                print("[WARNING] Gripper not calibrated. Calibrating...")
                self.calibrate()
                self.state.is_calibrated = True
            
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            self.connected = False
            print(f"[E_NOT_INITIALIZED] Connection failed: {e}")
            self._attempt_recovery()   

    def _initialize_gripperstate(self):
        try:
            self._send_command("STATUS")
            response = self._receive_response()[0]
            self.state.width_mm, self.state.speed, self.state.torque, self.state.min_width, self.state.max_width = map(float, response.strip().split(","))
        except Exception as E:
            print("[E_CMD_FAILED]. Try reconnecting...")

    def disconnect(self):
        if self.socket:
            self._send_command("BYE")
            response = self._receive_response()
            self.socket.close()
            self.socket = None
            self.connected = False
            print("[E_SUCCESS] Disconnected from gripper")

    def _send_command(self, cmd):
        """Send a string command over TCP."""
        if not self.connected:
            self._attempt_recovery()
        try:
            self.socket.sendall(cmd.encode('utf-8'))
            print(f"[COMMAND] Sent: {cmd}")
        except (BrokenPipeError, OSError):
            print("[E_NOT_INITIALIZED] Lost connection while sending.")
            self.connected = False
            self._attempt_recovery()

    def _receive_response(self):
        """Receive any number of lines until 'END' is seen or socket closes."""
        self.socket.settimeout(2.0)
        response_lines = []
        buffer = ""

        try:
            while True:
                chunk = self.socket.recv(1024).decode("utf-8")
                if not chunk:
                    break
                buffer += chunk

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if line == "END":
                        response = "\n".join(f"[E_SUCCESS] Received: {line}" for line in response_lines)
                        print(f"{response}")
                        return response_lines
                    if line:
                        response_lines.append(line)
        except socket.timeout:
            print("[E_TIMEOUT] Timeout while waiting for complete response.")

            return response_lines if response_lines else None
    
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

    def move_to(self, command):
        """Command the gripper to move to a specified width and speed."""
        try:
            match = re.match(r"move\(\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", command)
            if match:
                width_mm = float(match.group(1))
                speed = float(match.group(2)) if match.group(2) is not None else None
                with self.lock:
                    if not (self.state.min_width <= width_mm <= self.state.max_width):
                        print("[E_CMD_FAILED] Width out of range.")
                        return
                    if speed is not None:
                        self._send_command(f"MOVE({width_mm},{speed})")
                    else:
                        self._send_command(f"MOVE({width_mm})")
                    response = self._receive_response()

                    return response
            else:
                print(f"[E_NOT_ENOUGH_PARAMS] Invalid move command. Run help to know more.")
        except Exception as E:
            print(f"[E_CMD_FAILED] Invalid move command resulted in {E}. Run help to know more.")
    
    def get_pos(self):
        self._send_command("POS?")
        response = self._receive_response()[0]
        self.state.width_mm = map(float, response.strip().split(","))

        return response

    def get_speed(self):
        self._send_command("SPEED?")
        response = self._receive_response()[0]
        self.state.speed = map(float, response.strip().split(","))

        return response
    
    def get_force(self):
        self._send_command("FORCE?")
        response = self._receive_response()[0]
        self.state.torque = map(float, response.strip().split(","))

        return response

    def get_gripstate(self):
        self._send_command("GRIPSTATE?")
        response = self._receive_response()[0]
        self.state.gripstate = map(float, response.strip().split(","))

        return response

    def calibrate(self):
        self._send_command("CALIBRATE")
        response = self._receive_response()

        return response

    def grip(self, command):
        pattern = r"grip(?:\(\s*(?:(\d*\.?\d+)\s*(?:,\s*(\d*\.?\d+))?\s*(?:,\s*(\d*\.?\d+))?)?\s*\))?$"
        match = re.match(pattern, command)
        try:
            if match:
                force, part_width, speed_limit = None, None, None
                values = [float(v) for v in match.groups() if v is not None]
                if len(values)==3:
                    force, part_width, speed_limit = values[0], values[1], values[2]
                    self._send_command(f"GRIP({force},{part_width},{speed_limit})")
                elif len(values)==2:
                    force, part_width = values[0], values[1]
                    self._send_command(f"GRIP({force},{part_width})")
                elif len(values)==1:
                    force = values[0]
                    self._send_command(f"GRIP({force})")
                else:
                    self._send_command(f"GRIP()")
                response = self._receive_response()  

                return response               
            else:
                print("[E_NOT_ENOUGH_PARAMS] Invalid grip command. Run help to know usage guide.")
        except Exception as E:
            print(f"[E_CMD_FAILED] Invalid grip command resulted in {E}.\n Run help to know usage guide.")
            
    
    def release(self, command):
        try:
            match = re.match(r"release(?:\(\s*(?:(\d*\.?\d+)(?:\s*,\s*(\d*\.?\d+))?)?\s*\))?$", command, re.IGNORECASE)
            if match: # Type checking
                pull_back_distance, release_speed_limit = None, None
                values = [float(v) for v in match.groups() if v is not None]
                if len(values) == 2:
                    pull_back_distance, release_speed_limit = values[0], values[1]
                    self._send_command(f"RELEASE({pull_back_distance},{release_speed_limit})")
                elif len(values) == 1:
                    self._send_command(f"RELEASE({pull_back_distance})")
                    pull_back_distance = values[0]
                else:
                    self._send_command(f"RELEASE()")
                response = self._receive_response()   

                return response 
            else:
                print("[E_NOT_ENOUGH_PARAMS] Invalid release command. Run help to know more.")
        except Exception as E:
            print(f"[E_CMD_FAILED] Invalid release command resulted in {E}.\n Run help to know more.")

if __name__ == "__main__":
    driver = GripperDriver()
    run_cli_ui(driver)
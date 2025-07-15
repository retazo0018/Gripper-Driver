'''

    Copyright (c) 2025 Ashwin Murali <ashwin.murali99@gmail.com>
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

'''

import socket
import threading
import re
import time


class MockServer:
    '''
        MockServer simulates a gripper device over TCP/IP for testing the GripperDriver.
        
        This class acts as a stand-in for a physical two-finger gripper, allowing development
        and testing of the driver without real hardware. It listens for incoming socket
        connections, processes text-based GCL commands (e.g., MOVE, STATUS, CALIBRATE),
        and responds with simulated data.

        Features:
            - Accepts and parses incoming GCL commands from a client
            - Sends simulated multi-line responses (e.g., ACK, FIN, STATUS)
            - Maintains an internal GripperState object to track position, speed, and torque
            - Can simulate delays, state updates, and communication behavior of a real gripper
        
        Attributes:
            - host (str): IP address to bind the server socket
            - port (int): Port number to listen for client connections
    '''
    
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port

        # Default Values
        self.width = 110 # mm
        self.speed = 550 # mm/s
        self.torque = 5 # N
        self.min_width = 0.0 # mm
        self.max_width = 110.0 # mm
        self.is_connected = False 
        self.gripstate = 0
        self.pull_back_distance = 10 # mm; relative to current position
        self.release_speed_limit = 500 # mm/s
        self.PART_FALL_WIDTH_THRESHOLD = 15 # mm
        self.grip_speed_limit = 500 # mm/s
        self.grip_part_width = 25 # mm
    
    def to_status_string(self):
        '''
            Returns default parameters with its values as a string.
        '''
        
        return f"{self.width},{self.speed},{self.torque},{self.min_width},{self.max_width}"

    def to_calibration_string(self):
        '''
            Returns calibration parameters with its values as a string.
        '''
        
        return f"{self.min_width},{self.max_width}"

    def handle_client(self, conn, addr):
        ''' 
            Handles communication with a connected client.

            This method runs in a dedicated thread or process for each client connection.
            It receives GCL commands sent over the socket, processes them by updating the
            internal GripperState accordingly, and sends appropriate simulated responses
            (e.g., 'ACK', 'FIN', 'STATUS') back to the client.
        '''
        
        print(f"[SERVER] Connected by {addr}")
        with conn:
            self.gripstate = 1
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    command = data.decode().strip()
                    print(f"[SERVER] Received: {command}")

                    if command.startswith("MOVE"):
                        try:
                            conn.sendall(b"ACK MOVE\n")
                            match = re.match(r"MOVE\(\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", command)
                            if match:
                                self.speed = float(match.group(2)) if match.group(2) is not None else self.speed
                                time_to_move = abs(self.width - float(match.group(1))) / self.speed
                                self.width = float(match.group(1))
                                time.sleep(time_to_move)
                                self.gripstate = 6
                                conn.sendall(b"FIN MOVE\n")
                                conn.sendall(b"END\n")
                            else:
                                self.gripstate = 7
                                conn.sendall(b"ERROR\n")
                                conn.sendall(b"END\n")
                        except Exception as e:
                            self.gripstate = 7
                            error_msg = f"ERROR: {e}\n"
                            conn.sendall(error_msg.encode('utf-8'))
                            conn.sendall(b"END\n")

                    elif command == "STATUS":
                        response = self.to_status_string().encode()
                        conn.sendall(response)
                        conn.sendall(b"\nEND\n")

                    elif command == "POS?":
                        response = "POS="+str(self.width)+"\n"
                        conn.sendall(response.encode())
                        conn.sendall(b"END\n")
                    
                    elif command == "SPEED?":
                        response = "SPEED="+str(self.speed)+"\n"
                        conn.sendall(response.encode())
                        conn.sendall(b"END\n")
                    
                    elif command == "FORCE?":
                        response = "FORCE="+str(self.torque)+"\n"
                        conn.sendall(response.encode())
                        conn.sendall(b"END\n")
                    
                    elif command == "GRIPSTATE?":
                        response = "GRIPSTATE="+str(self.gripstate)+"\n"
                        conn.sendall(response.encode())
                        conn.sendall(b"END\n")

                    elif command == "CALIBRATE":
                        self.gripstate = 0
                        conn.sendall(b"ACK CALIBRATE\n")
                        self.min_width = 0.0
                        self.max_width = 110.0
                        conn.sendall(b"FIN CALIBRATE\n")
                        conn.sendall(b"END\n")
                    
                    elif command == "BYE":
                        self.is_connected = False
                        conn.sendall(b"ACK BYE\n")
                        conn.sendall(b"END\n")
                    
                    elif command == "STOP":
                        conn.sendall(b"ACK STOP\n")
                        self.gripstate = 0
                        conn.sendall(b"FIN STOP\n")
                        conn.sendall(b"END\n")
                    
                    elif command.startswith("GRIP"):
                        try:
                            conn.sendall(b"ACK GRIP\n")
                            self.gripstate = 1
                            pattern = r"GRIP(?:\(\s*((?:\d*\.?\d+\s*(?:,\s*\d*\.?\d+\s*)*)?)\))?$"
                            match = re.match(pattern, command)
                            if match is not None:
                                arg_str = match.group(1)
                                values = [float(x.strip()) for x in arg_str.split(",")] if arg_str else []
                                if len(values) == 3:
                                    self.torque, self.grip_part_width, self.grip_speed_limit = values[0], values[1], values[3]
                                elif len(values) == 2:
                                    self.torque, self.grip_part_width = values[0], values[1]
                                elif len(values) == 1:
                                    self.torque = values[0]

                                if self.width - self.grip_part_width >= self.PART_FALL_WIDTH_THRESHOLD:
                                    self.gripstate=2 # NO PART
                                    conn.sendall(b"No part detected between the fingers. Set width between the fingers and width of the part correctly.\n")
                                    conn.sendall(b"ACK NO PART\n")
                                    conn.sendall(b"END\n")
                                else:
                                    self.gripstate=4 # HOLDING
                                    conn.sendall(b"ACK HOLDING\n")
                                    conn.sendall(b"FIN GRIP\n")
                                    conn.sendall(b"END\n")
                            else:
                                self.gripstate = 7
                                conn.sendall(b"ERROR\n")
                                conn.sendall(b"END\n")
                        except Exception as e:
                                self.gripstate = 7
                                error_msg = f"ERROR: {e}\n"
                                conn.sendall(error_msg.encode('utf-8'))
                                conn.sendall(b"END\n")
                        
                    elif command.startswith("RELEASE"):
                        try:
                            conn.sendall(b"ACK RELEASE\n")
                            match = re.match(r"release(?:\(\s*(?:(\d*\.?\d+)(?:\s*,\s*(\d*\.?\d+))?)?\s*\))?$", command, re.IGNORECASE)
                            if match and self.gripstate in [2, 3, 4]:
                                values = [float(v) for v in match.groups() if v is not None]
                                if len(values) == 2:
                                    self.pull_back_distance, self.release_speed_limit = values[0], values[1]
                                elif len(values) == 1:
                                    self.pull_back_distance = values[0]

                                self.gripstate = 5
                                time.sleep(self.pull_back_distance / (self.release_speed_limit/100)) # Diving by 100 to show difference
                                self.gripstate = 0
                                conn.sendall(b"FIN RELEASE\n")
                                conn.sendall(b"END\n")
                            else:
                                self.gripstate = 7
                                conn.sendall(b"ERROR. Was the part gripped?\n")
                                conn.sendall(b"END\n")
                        except Exception as e:
                            self.gripstate = 7
                            error_msg = f"ERROR: {e}\n"
                            conn.sendall(error_msg.encode('utf-8'))
                            conn.sendall(b"END\n")
                            
                    else:
                        self.gripstate = 7
                        conn.sendall(b"ERROR: Unknown command\n")
                        conn.sendall(b"END\n")

                except ConnectionResetError:
                    self.gripstate = 7
                    print("[SERVER] Connection reset by client.")
                    break

    def start(self):
        '''
            Starts the socket server for the mock gripper to enable communication with client.
        '''
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            print(f"[SERVER] Gripper server listening on {self.host}:{self.port}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    server = MockServer()
    server.start()

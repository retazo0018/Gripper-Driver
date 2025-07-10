# Gripper Simulator

import socket
import threading
import re
import time


class MockServer:
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
    
    def to_status_string(self):
        return f"{self.width},{self.speed},{self.torque},{self.min_width},{self.max_width}"

    def to_calibration_string(self):
        return f"{self.min_width},{self.max_width}"

    def handle_client(self, conn, addr):
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
                        except:
                            self.gripstate = 7
                            conn.sendall(b"ERROR\n")
                            conn.sendall(b"END\n")

                    elif command == "STATUS":
                        self.gripstate = 0
                        response = self.to_status_string().encode()
                        conn.sendall(response)
                        conn.sendall(b"\nEND\n")

                    elif command == "POS?":
                        self.gripstate = 0
                        response = "POS="+str(self.width)+"\n"
                        conn.sendall(response.encode())
                        conn.sendall(b"END\n")
                    
                    elif command == "SPEED?":
                        self.gripstate = 0
                        response = "SPEED="+str(self.speed)+"\n"
                        conn.sendall(response.encode())
                        conn.sendall(b"END\n")
                    
                    elif command == "FORCE?":
                        self.gripstate = 0
                        response = "FORCE="+str(self.torque)+"\n"
                        conn.sendall(response.encode())
                        conn.sendall(b"END\n")
                    
                    elif command == "GRIPSTATE?":
                        response = "GRIPSTATE="+str(self.gripstate)+"\n"
                        conn.sendall(response.encode())
                        conn.sendall(b"END\n")
                        self.gripstate = 0

                    elif command == "CALIBRATE":
                        self.gripstate = 0
                        conn.sendall(b"ACK CALIBRATE\n")
                        self.min_width = 0.0
                        self.max_width = 110.0
                        conn.sendall(b"FIN CALIBRATE\n")
                        conn.sendall(b"END\n")
                    
                    elif command == "BYE":
                        self.gripstate = 0
                        self.is_connected = False
                        conn.sendall(b"ACK BYE\n")
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

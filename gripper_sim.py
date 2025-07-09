# Gripper Simulator

import socket
import threading


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
    
    def to_status_string(self):
        return f"{self.width},{self.speed},{self.torque},{self.min_width},{self.max_width}"

    def to_calibration_string(self):
        return f"{self.min_width},{self.max_width}"

    def handle_client(self, conn, addr):
        print(f"[SERVER] Connected by {addr}")
        with conn:
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    command = data.decode().strip()
                    print(f"[SERVER] Received: {command}")

                    if command.startswith("MOVE"):
                        try:
                            _, value = command.split()
                            self.width = float(value)
                            conn.sendall(b"OK")
                        except:
                            conn.sendall(b"ERROR")

                    elif command == "STATUS":
                        response = self.to_status_string().encode()
                        conn.sendall(response)

                    elif command == "CALIBRATE":
                        self.min_width = 0.0
                        self.max_width = 100.0
                        conn.sendall(self.to_calibration_string().encode())

                    else:
                        conn.sendall(b"ERROR: Unknown command")

                except ConnectionResetError:
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

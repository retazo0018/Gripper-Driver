import time
import ast
from gripper_driver import GripperDriver
import re


if __name__ == "__main__":
    driver = GripperDriver()
    time.sleep(1)
    print("Ready for commands. Type 'help' for available commands.")

    while True:
        command = input("> ").strip().lower()

        if command.startswith("move"):
            try:
                match = re.match(r"move\(\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", command)
                if match:
                    width = float(match.group(1))
                    speed = float(match.group(2)) if match.group(2) is not None else None
                    driver.move_to(width, speed)
                else:
                    print("Invalid move command. Usage: move(<float>, <float>)")
            except (IndexError, ValueError):
                print("Invalid move command. Usage: move(<float>, <float>)")
        
        elif command == "pos?":
            driver.get_pos()
        
        elif command == "speed?":
            driver.get_speed()
        
        elif command == "force?":
            driver.get_force()
        
        elif command == "gripstate?":
            driver.get_gripstate()
        
        elif command == "bye":
            driver.disconnect()
            
        elif command == "help":
            print("Available commands:")
            print("move(<float>, <float>)   - Move gripper to position. Specify width and speed")
            print("pos?                     - the current position of the gripper jaws (open width)")
            print("speed?                   - Get current speed in mm/s")
            print("force?                   - Get current force value in N")
            print("gripstate?               - Get current gripper state")
            print("bye                      - Disconnect from gripper")
            print("exit                     - Exit the CLI")

        elif command == "exit":
            print("Exiting.")
            break

        else:
            print("Unknown command. Type 'help' for available commands.")
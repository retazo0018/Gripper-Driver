import time


def run_cli_ui(driver):
    time.sleep(1)
    print("Ready for commands. Type 'help' for available commands.")

    while True:
        command = input("> ").strip().lower()

        if command.startswith("move"):
            driver.move_to(command)
            
        elif command == "calibrate":
            driver.calibrate()

        elif command == "pos?":
            driver.get_pos()
        
        elif command == "speed?":
            driver.get_speed()
        
        elif command == "force?":
            driver.get_force()
        
        elif command == "gripstate?":
            driver.get_gripstate()
        
        elif command.startswith("grip"):
            driver.grip(command)

        elif command.startswith("release"):
            driver.release(command)
        
        elif command == "bye":
            driver.disconnect()
        
        elif command == "stop":
            driver.stop()
            
        elif command == "help":
            print("Available commands:")
            print("move(<WIDTH>, <SPEED>) or move(<WIDTH>)                                                      - Move gripper to position.")
            print("calibrate                                                                                    - Calibrate the gripper with default min and max width")           
            print("pos?                                                                                         - the current position of the gripper jaws (open width)")
            print("speed?                                                                                       - Get current speed in mm/s")
            print("force?                                                                                       - Get current force value in N")
            print("gripstate?                                                                                   - Get current gripper state")
            print("grip(<FORCE>, <PART_WIDTH>, <SPEED_LIMIT>) or grip()                                         - Grip a part from the current position")
            print("release(<PULL_BACK_DISTANCE>, <SPEED_LIMIT>) or release(<PULL_BACK_DISTANCE>) or release()   - Release the part from the gripper")
            print("bye                                                                                          - Disconnect from gripper")
            print("stop                                                                                         - Returns to IDLE state")
            print("exit                                                                                         - Exit the CLI")

        elif command == "exit":
            print("Exiting.")
            break

        else:
            print("[E_CMD_UNKNOWN] Unknown command. Type 'help' for available commands.")
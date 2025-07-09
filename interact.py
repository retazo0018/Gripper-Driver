import time
from gripper_driver import GripperDriver


if __name__ == "__main__":
    driver = GripperDriver()
    time.sleep(1)
    driver.move_to(50)
    driver.get_status()

    # Execute a sequence of Actions
    #sequence = [("MOVE", 80), ("WAIT", 0.5), ("MOVE", 10), ("WAIT", 0.2)]
    #driver.execute_sequence(sequence)
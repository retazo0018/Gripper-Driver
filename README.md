# Gripper Driver
Program a driver for a two-finger gripper used in bin picking applications. Goal is to create a Python program that receives a width in millimeters and controls the gripper to maintain that distance between its two fingers. Program should also include any other features relevant for a driver. 

See [task overview](task.md) to know the details of this challenge.

# Getting-started
- Run `python gripper_sim.py` in a terminal launches the socket server that controls the mock gripper.

- Run `python interact.py` that starts a client that communicates with the gripper. This script sends commands to the gripper server. Type `help` in the CLI to know the list of commands and their purposes.

# Codebase
- `gripper_sim.py` simulates the gripper. The gripper is configured with the default configurations from the manufacturer's documentation. 

- `gripper_driver.py` contains the driver implementation and the solution for this challenge.
    - Maintains an internal state of the gripper.
    - Manages TCP/IP communication with the gripper, handling the transmission of commands and reception of responses to ensure reliable control.



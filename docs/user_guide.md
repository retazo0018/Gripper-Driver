# 📘 User Guide

This document provides detailed usage guidelines for each of the commands available in this framework. Please note:

- **All commands are not case-sensitive** — you can use uppercase, lowercase, or any combination.
- Commands can be used in any context supported by the framework.

## `pos?`

Returns the current position of the gripper — the width between the two fingers in mm.

**Syntax:**  `pos?`

**Expected Output:**
[COMMAND] Sent: POS?
[E_SUCCESS] Received: POS="VALUE"

## `speed?`

Returns the current speed of the gripper in mm/s.

**Syntax:**  `speed?`

**Expected Output:**  
[COMMAND] Sent: SPEED?  
[E_SUCCESS] Received: SPEED="VALUE"

## `force?`

Returns the current force/torque of the gripper in N. Useful to grip the part.

**Syntax:**  `force?`

**Expected Output:**  
[COMMAND] Sent: FORCE?  
[E_SUCCESS] Received: FORCE="VALUE"

## `gripstate?`

Returns the current state of the gripper.

**Syntax:**  `gripstate?`

**Expected Output:**  
[COMMAND] Sent: GRIPSTATE?  
[E_SUCCESS] Received: GRIPSTATE="VALUE"

## `calibrate`

Calibrates the gripper to its default min (0.0 mm) and max width (110.0 mm) respectively.

**Syntax:**  `calibrate`

**Expected Output:**  
[COMMAND] Sent: CALIBRATE  
[E_SUCCESS] Received: ACK CALIBRATE  
[E_SUCCESS] Received: FIN CALIBRATE

## `move`

Moves the gripper to the specified width and speed.

**Syntax:**  
`move(WIDTH, SPEED)` or `move(WIDTH)`  
where `WIDTH` should be in mm and `SPEED` should be in mm/s.

**Example:**  
`move(20, 500)`

**Expected Output:**  
[COMMAND] Sent: MOVE(20.0,500.0)  
[E_SUCCESS] Received: ACK MOVE  
[E_SUCCESS] Received: FIN MOVE

**Error:**  
Wrong input `move` results in:  
`[E_NOT_ENOUGH_PARAMS] Invalid move command. Run help to know usage.`

Out of range width input results in:
`[E_CMD_FAILED] Width out of range.`

## `grip`

Grips a part at the current position.

**Syntax:**  
`grip`  
or  
`grip(FORCE)`  
or  
`grip(FORCE, GRIP_PART_WIDTH)`  
or  
`grip(FORCE, GRIP_PART_WIDTH, GRIP_SPEED_LIMIT)`

- `FORCE`: Torque to grip the part in N  
- `GRIP_PART_WIDTH`: Width in mm of the part that needs to be gripped  
- `GRIP_SPEED_LIMIT`: Speed limit in mm/s
- Default values are assumed if fewer arguments are provided.

**Usage Example:**  
`grip(2, 20)`

**Expected Output:**  
[COMMAND] Sent: GRIP(2.0,20.0)  
[E_SUCCESS] Received: ACK GRIP  
[E_SUCCESS] Received: ACK HOLDING  
[E_SUCCESS] Received: FIN GRIP

**Other Examples:**  
`grip(2, 20, 500)`,
`grip`


**Note:**  
If you try to grip a part whose width is lower or higher than the current width of the gripper, you will receive:  
[E_SUCCESS] Received: ACK GRIP
[E_SUCCESS] Received: No part detected between the fingers. Set width between the fingers and width of the part correctly.  
[E_SUCCESS] Received: ACK NO PART

In this case, move the gripper according to the width of the part that needs to be gripped and try again.

## `release`

Releases the gripped part from the gripper.

**Syntax:**  
`release()`  
or  
`release(PULL_BACK_DISTANCE)`  
or  
`release(PULL_BACK_DISTANCE, SPEED_LIMIT)`

- `PULL_BACK_DISTANCE`: Distance the gripper needs to move further apart after release. 
- `SPEED_LIMIT`: Speed at which the release should take place  
- Default values are assumed if fewer arguments are provided.

**Example Usage:**  
`release(10)`

**Expected Output:**  
[COMMAND] Sent: RELEASE()  
[E_SUCCESS] Received: ACK RELEASE  
[E_SUCCESS] Received: FIN RELEASE

**Other Examples:**  
`release`,
`release(20, 500)`

**Note:**  
When `release` is executed without first gripping a part, the following is observed:  
[COMMAND] Sent: RELEASE()  
[E_SUCCESS] Received: ACK RELEASE  
[E_SUCCESS] Received: ERROR. Was the part gripped?

## `stop`

Returns the gripper to the IDLE state (0).

**Syntax:**  
`stop`

**Expected Output:**  
[COMMAND] Sent: STOP  
[E_SUCCESS] Received: ACK STOP  
[E_SUCCESS] Received: FIN STOP  
[E_SUCCESS] Returned to IDLE state.

## `bye`

Disconnects the client from the gripper.

**Syntax:**  
`bye`

**Expected Output:**  
[COMMAND] Sent: BYE  
[E_SUCCESS] Received: ACK BYE  
[E_SUCCESS] Disconnected from gripper

## ``exit``
Exits the CLI

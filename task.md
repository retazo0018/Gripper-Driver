# Challenge Overview
Goal is to create a Python program that receives a width in millimeters and controls the gripper to maintain that distance between its two fingers. Program should also include any other features relevant for a driver. 

## Gripper Details
The driver must be implemented based on the manufacturer's documentation given [here](https://weiss-robotics.com/servo-electric/wsg-series/product/wsg/selectVariant/wsg-50-110/).

## Tasks
### Driver setup
- Define the structure of your driver, including its states, functions, and features needed for a bin picking application Your code will be part of a larger framework that controls a 6-axis robotic arm, an RGB-D camera, and a GUI. This framework will use your driver to interact with the gripper.

### Communication
- The communication with the gripper should be via TCP/IP protocol, using sockets.

### Available information
- Allow the framework to query your driver for the gripper's current width (position) and other relevant information such as speed and torque.

### Recovery behavior
- Ensure your driver can recover communication with the gripper if the cable is disconnected or there is a brief power interruption.

### Calibration
- Implement a function that calibrates your gripper to update the maximum and minimum distances according to its physical limits.

## Additional Notes
- Use Python as the programming language for this challenge.
- Focus on clear and well-structured code. Modularize your code into functions for readability and reusability.
- While visualization is not the primary goal, feel free to display the movement steps in a readable format (e.g., print statements).
- Make sure to use local Git to track your changes.
- You are allowed to use frameworks, libraries, and packages as you feel they are useful for this task. There are no limits for this.
- Write unit tests with a framework of your choice to ensure the functionality of your project.
- We don't assume you have a gripper with you, so you don't have to send a driver that you have tested. We are more interested in your way of thinking, not if your driver literally works.

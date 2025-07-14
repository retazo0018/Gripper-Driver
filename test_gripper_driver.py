# Unit Test to test the framework

from gripper_driver import GripperDriver
from gripper_sim import MockServer 
import threading
import pytest
import time

@pytest.fixture(scope="session", autouse=True)
def start_gripper_server():
    server = MockServer()
    thread = threading.Thread(target=server.start, daemon=True)
    thread.start()

    time.sleep(2)  # Wait for the server to initialize
    yield

def test_move_to(capsys):
    driver = GripperDriver()
    driver.move_to(100, 500)
    captured = capsys.readouterr()
    assert "FIN MOVE" in captured.out

def test_get_pos(capsys):
    driver = GripperDriver()
    driver.get_pos()
    captured = capsys.readouterr()
    assert "POS=" in captured.out

def test_get_speed(capsys):
    driver = GripperDriver()
    driver.get_speed()
    captured = capsys.readouterr()
    assert "SPEED=" in captured.out

def test_get_gripperstate(capsys):
    driver = GripperDriver()
    driver.get_gripstate()
    captured = capsys.readouterr()
    assert "GRIPSTATE=" in captured.out

def test_get_force(capsys):
    driver = GripperDriver()
    driver.get_force()
    captured = capsys.readouterr()
    assert "FORCE=" in captured.out

def test_calibrate(capsys):
    driver = GripperDriver()
    driver.calibrate()
    captured = capsys.readouterr()
    assert "FIN CALIBRATE" in captured.out

def test_bye(capsys):
    driver = GripperDriver()
    driver.disconnect()
    captured = capsys.readouterr()
    assert "ACK BYE" in captured.out

import time
from communication.serial.arduino_controller import ArduinoController
from communication.serial.commands import BuzzCommand

# Example serial communication:
with ArduinoController(port="/dev/ttyACM0") as arduino:
    arduino.send_command(BuzzCommand(duration_ms=1000, frequency=1000))
    time.sleep(2)
    arduino.send_command(BuzzCommand(duration_ms=500, frequency=3000))


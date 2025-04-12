from communication.serial.arduino_controller import ArduinoController
from communication.serial.commands import BuzzCommand

# Example serial communication:
with ArduinoController(port="/dev/ttyACM0") as arduino:
    arduino.send_command(BuzzCommand(duration_ms=1000, frequency=1000))
    responses = arduino.read_response()
    for response in responses:
        print(f"Arduino: {response}")


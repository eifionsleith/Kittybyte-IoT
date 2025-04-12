import time
from typing import Optional, List
from serial import Serial, SerialException

from .commands import ArduinoCommand

class ArduinoController:
    """Controller for serial communication with the Arduino"""

    def __init__(self,
                 port: str,
                 rate: int = 9600,
                 timeout: int = 1):
        """
        Initialize the Arduino controller.

        Args:
            port (str): Serial port to connect to, e.g. /dev/ttyACM0
            rate (int): Rate for serial communication, defaults to 9600
            timeout (int): Read timeout in seconds, defaults to 1 second
        """
        self._port = port
        self._rate = rate
        self._timeout = timeout
        self._connection: Optional[Serial] = None

    def connect(self) -> bool:
        """
        Open the serial connection to the Arduino.

        Returns:
            bool: True if successful.
        """
        try:
            self._connection = Serial(self._port, self._rate, self._timeout)
            time.sleep(2)
            return True
        except SerialException as e:
            print(f"Error connection to Arduino: {e}")
            return False  # TODO: Exceptions?

    def disconnect(self) -> None:
        """
        Closes the serial connection.
        """
        if self._connection and self._connection.is_open:
            self._connection.close()
            self._connection = None
        else:
            print("Attempt to disconnect non-existant serial connection.")

    def send_command(self, command: ArduinoCommand) -> bool:
        """
        Send a command to the Arduino.

        Args:
            command (str): String encoded command to send.

        Returns:
            bool: True if the command was sent, False otherwise.
        """
        if not self._connection or not self._connection.is_open:
            print("Error: Not connected to Arduino")
            return False

        try:
            str_command = f"{command.to_serial_string()}\n"
            self._connection.write(str_command.encode("utf-8"))
            print(f"Sent command: {command}")
            return True
        except SerialException as e:
            print(f"Error sending command: {e}")
            return False

    def read_response(self, timeout: float = 5.0) -> List[str]:
        """
        Read response from Arduino.

        Args:
            timeout (float): Maximum time to wait for responses in seconds, defaults to 5.0

        Returns:
            List[str]: List of responses from Arduino
        """
        if not self._connection or not self._connection.is_open:
            print("Error: Not connected to Arduino.")
            return []

        responses = []
        end_time = time.time() + timeout

        while time.time() < end_time:
            if self._connection.in_waiting:
                line = self._connection.readline().decode("utf-8").strip()
                if line:
                    responses.append(line)
            else:
                time.sleep(0.1)

        return responses

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


import time
from typing import Optional
from serial import Serial, SerialException

from .commands import ArduinoCommand
from .protocol import Protocol

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
            self._connection = Serial(self._port, self._rate, timeout=self._timeout)
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
            binary_command = command.encode()
            self._connection.reset_input_buffer()
            self._connection.write(binary_command)
            self._connection.flush()
            return self._wait_for_ok()
        except SerialException as e:
            print(f"Error sending command: {e}")
            return False

    def _wait_for_ok(self) -> bool:
        """
        Waits for MSG_OK response from Arduino, indicating acknowledgement of command.

        Returns:
            bool: True if acknowledged, False on timeout or error
        """
        if not self._connection or not self._connection.is_open:
            print("Error: Not connected to Arduino")
            return False

        start_time = time.time()

        while time.time() - start_time < self._timeout:
            if self._connection.in_waiting:
                response = self._connection.read(1)
                if response and response[0] == Protocol.MSG_OK:
                    return True

            time.sleep(0.01)

        return False

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


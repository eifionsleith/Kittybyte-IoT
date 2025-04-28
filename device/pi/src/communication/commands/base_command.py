from abc import ABC, abstractmethod
from typing import Any

class ArduinoCommand(ABC):
    """
    Abstract base class for all commands that will be 
    sent from the Pi to the Arduino.
    """

    @abstractmethod
    def get_command_id(self) -> int:
        """
        Returns the unique byte ID for this command as defined
        in the protocol.

        This ID is used in the packet header.

        Returns:
            int: The command ID (0-255)
        """
        ...

    @abstractmethod
    def get_payload(self) -> bytes:
        """
        Encodes the command's paramaters into a binary payload.

        Returns:
            bytes: The binary payload data. For no payload, b''.
        """
        ...

    @abstractmethod 
    def parse_response(self, response_id: int, payload: bytes) -> Any:
        """
        Parses the payload of a response packet receives from 
        the Arduino that corresponds to this command.

        The implementation should check response_id and interpret
        the payload bytes accordingly.

        Args:
            response_id (int): The response ID received from the Arduino,
                               e.g. arduino_protocol.R_NOTIFY_TASK_COMPLETE.
            payload (bytes): The raw payload bytes receives in the response packet.

        Returns:
            Any: A parsed representation of the response data.
        """
        ...


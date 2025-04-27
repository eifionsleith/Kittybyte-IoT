import struct
import logging

from .base_command import ArduinoCommand
from .. import arduino_protocol
from ..arduino_service import ArduinoProtocolError, ArduinoResourceBusyError

logger = logging.getLogger(__name__)

class SimpleBuzzCommand(ArduinoCommand):
    """
    Represents the BUZZER_SIMPLE command to play a single
    tone at a specific frequency for a given duration.
    """
    def __init__(self, frequency: int, duration_ms: int) -> None:
        """
        Initializes the SimpleBuzzCommand.

        Args:
            frequency (int): The frequency of the tone, in Hz.
            duration_ms (int): The duration of the tone, in milliseconds.

        Raises:
            ValueError: If any params are outside the valid range for uint16_t.
        """
        UINT16_T_MAX_VALUE = 65535
        if not (0 <= frequency <= UINT16_T_MAX_VALUE):
            raise ValueError(f"Frequency ({frequency}) is outside the valid range.")
        if not (0 <= duration_ms <= UINT16_T_MAX_VALUE):
            raise ValueError(f"Duration ({duration_ms}) is outside the valid range.")

        self._frequency = frequency
        self._duration_ms = duration_ms

    def get_command_id(self) -> int:
        """Returns the command ID for BUZZER_SIMPLE."""
        return arduino_protocol.CMD_BUZZER_SIMPLE

    def get_payload(self) -> bytes:
        """
        Encodes the frequency and duration into the command payload.
        """
        # Big-Endian (>)
        payload = struct.pack('>HH', self._frequency, self._duration_ms)
        return payload

    def parse_response(self, response_id: int, payload: bytes) -> bool:
        """
        Parses the response received from the SimpleBuzzCommand.

        Args:
            response_id (int): The response ID from the Arduino.
            payload (bytes): The payload bytes from the response.

        Returns:
            bool: True if the response indicates the task is complete.
                False otherwise.

        Raises:
            ArduinoProtocolError: If the response indicates an error on
                the Arduino's side.
        """
        # -- Success Responses
        if response_id == arduino_protocol.R_NOTIFY_COMMAND_RECEIVED:
            return False

        elif response_id == arduino_protocol.R_NOTIFY_TASK_COMPLETE:
            return True
        
        # -- Error Responses
        elif response_id == arduino_protocol.R_ERROR_UNKNOWN_COMMAND:
            error_msg = "Arduino reported ERROR_UNKNOWN_COMMAND for SimpleBuzz."
            logger.error(error_msg)
            raise ArduinoProtocolError(error_msg)

        elif response_id == arduino_protocol.R_ERROR_INVALID_PAYLOAD:
            error_msg = "Arduino reported ERROR_INVALID_PAYLOAD for SimpleBuzz."
            logger.error(error_msg)
            raise ArduinoProtocolError(error_msg)

        elif response_id == arduino_protocol.R_ERROR_RESOURCE_BUSY:
            error_msg = "Arduino reported ERROR_RESOURCE_BUSY for SimpleBuzz. Buzzer is currently busy."
            logger.error(error_msg)
            raise ArduinoResourceBusyError(error_msg)

        elif response_id == arduino_protocol.R_ERROR_TASK_FAILED:
            error_msg = "Arduino reported ERROR_TASK_FAILED for SimpleBuzz."
            logger.error(error_msg)
            raise ArduinoProtocolError(error_msg)

        else:
            error_msg = f"Received unexpected response ID {hex(response_id)} for SimpleBuzz."
            logger.error(error_msg)
            raise ArduinoProtocolError(error_msg)


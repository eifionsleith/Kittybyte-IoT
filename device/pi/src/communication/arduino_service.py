import logging
import time
import serial
import itertools
import threading
from enum import Enum, auto
from typing import Any, Callable, Dict, Optional

from . import arduino_protocol

logger = logging.getLogger(__name__)

# --- Custom Exceptions ---
class ArduinoCommunicationError(Exception):
    """Base class for errors related to Arduino communication."""
    ...

class ArduinoResourceBusyError(ArduinoCommunicationError):
    """Raised when the requested resource (e.g. buzzer) is busy."""

class ArduinoTimeoutError(ArduinoCommunicationError):
    """Raised when a communication timeout occurs."""
    ...

class ArduinoProtocolError(ArduinoCommunicationError):
    """Raised when there's an error related to the communication protocol."""
    ...

class ArduinoChecksumError(ArduinoProtocolError):
    """Raised when a checksum mismatch occurs."""
    ...

class ArduinoPacketSizeError(ArduinoProtocolError):
    """Raised when a packet size exceeds maximum allowed by the protocol."""
    ...

class ArduinoConnectionError(ArduinoCommunicationError):
    """Raised for issues related to the serial connection state."""
    ...

# --- Packet Parsing State Machine ---
class ParseState(Enum):
    """States forn the incoming packet parsing state machine."""
    WAITING_FOR_START = auto()
    READING_PACKET_ID = auto()
    READING_RESPONSE_ID = auto()
    READING_LENGTH = auto()
    READING_PAYLOAD = auto()
    VALIDATING_CHECKSUM = auto()

# --- Arduino Service Class ---
class ArduinoService:
    def __init__(self, port: str, baud_rate: int, timeout: float = 1.0) -> None:
        """
        Initialzies the ArduinoService.

        Args:
            port (str): Serial port the Arduino is connected to, e.g. "/dev/ttyACM0".
            baud_rate (int): The baud rate for serial communication.
            timeout (float): Default timeout for serial read operations.
                Defaults to 1.0.
        """
        self._port = port
        self._baud_rate = baud_rate
        self._default_timeout = timeout
        self._connection: Optional[serial.Serial] = None

        # Parsing state machine variables
        self._parse_state = ParseState.WAITING_FOR_START
        self._current_packet_id: Optional[int] = None
        self._current_response_id: Optional[int] = None
        self._expected_payload_length = 0 
        self._payload_buffer = bytearray()
        self._bytes_recieved_count = 0 
        self._packet_buffer = bytearray()

        # Response handling
        self._packet_id_generator = itertools.cycle(range(256))
        self._pending_commands: Dict[int, Dict[str, Any]] = {}
        self._pending_commands_lock = threading.Lock()

    def connect(self) -> bool:
        """
        Opens the serial connection to the Arduino.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        if self._connection and self._connection.is_open:
            logger.info("Arduino connection already open.")
            return True

        try:
            self._connection = serial.Serial(
                    self._port,
                    self._baud_rate,
                    timeout=self._default_timeout
                    )
            time.sleep(2)  # Wait for Arduino initialization -> Could be replaced with a handshake.

            # Reset any stale data
            self._connection.reset_input_buffer()
            self._reset_parser_state()
            self._pending_commands.clear()
            
            logger.info(f"Connected successfully to Arduino on port {self._port} at rate {self._baud_rate}.")
            return True
        except serial.SerialException as e:
            logger.error(f"Could not connect to Arduino on port {self._port}: {e}")
            self._connection = None
            return False
        except Exception as e:
            logger.exception(f"An unexpected error occured during Arduino connection on port {self._port}")
            self._connection = None
            return False
    
    def disconnect(self):
        """Closes the serial connection."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            self._connection = None
            logger.info(f"Arduino connection on port {self._port} closed.")
            self._reset_parser_state()
            self._pending_commands.clear()
        else:
            self._connection = None
            logger.info("Attempting to close non-existant connection.")

    def is_connected(self) -> bool:
        """Checks if the serial connection is currently open."""
        return self._connection is not None and self._connection.is_open

    def _reset_parser_state(self):
        """Resets the parser state machine variables."""
        self._parse_state = ParseState.WAITING_FOR_START
        self._current_packet_id = None
        self._current_response_id = None
        self._expected_payload_length = 0 
        self._payload_buffer.clear()
        self._bytes_recieved_count = 0 
        self._packet_buffer.clear()

    def _parse_byte(self, byte: int) -> Optional[Dict[str, Any]]:
        """
        Processes a single byte from the serial stream using a state 
        machine to assemble incoming packets.

        Args:
            byte (int): The byte received from the serial port.

        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the parsed 
                                      packet if a complete packet is received,
                                      otherwise None.
        """
        self._packet_buffer.append(byte)

        if self._parse_state == ParseState.WAITING_FOR_START:
            if byte == arduino_protocol.START_BYTE:
                self._parse_state = ParseState.READING_PACKET_ID
                # Ensure no stale data is present as we already added without checks
                self._packet_buffer.clear()
                self._packet_buffer.append(byte)
            else:
                # Garbage data, discard
                self._packet_buffer.clear()

        elif self._parse_state == ParseState.READING_PACKET_ID:
            self._current_packet_id = byte
            self._parse_state = ParseState.READING_RESPONSE_ID

        elif self._parse_state == ParseState.READING_RESPONSE_ID:
            self._current_response_id = byte
            self._parse_state = ParseState.READING_LENGTH

        elif self._parse_state == ParseState.READING_LENGTH:
            self._expected_payload_length = byte
            if self._expected_payload_length > arduino_protocol.MAX_PAYLOAD_SIZE:
                logger.warning(f"Received invalid or excessive payload length ({self._expected_payload_length}) from Arduino. \
                        Resetting buffer.")
                self._reset_parser_state()
            else:
                self._bytes_recieved_count = 0 
                self._payload_buffer.clear()
                if self._expected_payload_length == 0:
                    # No payload expected, skip
                    self._parse_state = ParseState.VALIDATING_CHECKSUM
                else:
                    self._parse_state = ParseState.READING_PAYLOAD
        
        elif self._parse_state == ParseState.READING_PAYLOAD:
            self._payload_buffer.append(byte)
            self._bytes_recieved_count += 1 
            if self._bytes_recieved_count == self._expected_payload_length:
                self._parse_state = ParseState.VALIDATING_CHECKSUM

        elif self._parse_state == ParseState.VALIDATING_CHECKSUM:
            received_checksum = byte
            # Final byte is the checksum, so ignore that with a slice.
            calculated_checksum = arduino_protocol.calculate_checksum(bytes(self._packet_buffer[0:-1]))
            is_valid = received_checksum == calculated_checksum
            
            parsed_packet = {
                    "packet_id": self._current_packet_id,
                    "response_id": self._current_response_id,
                    "payload_length": self._expected_payload_length,
                    "payload": bytes(self._payload_buffer),
                    "received_checksum": received_checksum,
                    "calculated_checksum": calculated_checksum,
                    "raw_bytes": bytes(self._packet_buffer).hex()
                    }
            self._reset_parser_state()
            
            if is_valid:
                logger.debug(f"Successfully parsed valid packet from Arduino: {parsed_packet}")
                return parsed_packet
            else:
                logger.warning(f"Checksum mismatch in packet from Arduino - discarding: {parsed_packet}")
        
        # Nothing to return yet, only state VALIDATING_CHECKSUM will return a packet.
        # Until then we're just running this in a loop.
        return None

    def process_incoming_data(self):
        """
        Reads all available bytes from the serial buffer, processes 
        them through the state machine and handles any complete packets 
        found by triggering appropriate callbacks.

        This method should be called in the main loop.
        """
        if not self.is_connected():
            logger.debug("Arduino not connected, skipping data processing.")
            return

        try:
            bytes_to_read = self._connection.in_waiting # pyright: ignore[reportOptionalMemberAccess]
            if bytes_to_read > 0:
                for _ in range(bytes_to_read):
                    byte = self._connection.read(1) # pyright: ignore[reportOptionalMemberAccess]
                    if byte:
                        parsed_packet = self._parse_byte(byte[0])
                        if parsed_packet:
                            self._handle_received_packet(parsed_packet)
                    else:
                        # This shouldn't happen.
                        logger.warning("Arduino read unexpected returned None during process_incoming_data.")
                        break

        except serial.SerialException as e:
            logger.error(f"Serial exception during data processing: {e}")

        except Exception as e:
            logger.exception("An unexpected error occured trying to read bytes from Arduino.")

    def _handle_received_packet(self, packet: Dict[str, Any]):
        """
        Handles a complete received packet (valid or invalid checksum).
        If valid and matching a pending command, will trigger the callback.
        """
        logger.debug(f"Packet: {packet}")
        packet_id = packet["packet_id"]
        response_id = packet["response_id"]
        payload = packet["payload"]
        logger.debug(f"Processing a received packet {packet_id}: {packet}")
        logger.debug(f"And response_id {response_id}")

        with self._pending_commands_lock:
            pending_command_info = self._pending_commands.get(packet_id, None)

        if pending_command_info:
            logger.debug("Found pending command for packet ID {packet_id}. Triggering callback.")

            # If the response_id is R_NOTIFY_COMMAND_RECEIVED we still expect further responses.
            if response_id != arduino_protocol.R_NOTIFY_COMMAND_RECEIVED:
                with self._pending_commands_lock:
                    self._pending_commands.pop(packet_id)

            callback = pending_command_info.get("callback")
            if callback:
                try:
                    callback(packet_id, response_id, payload)
                except Exception:
                    logger.exception(f"Error executing callback for packet {packet_id}.")
            else:
                logger.debug(f"No callback registered for packet {packet_id}.")

        else:
            # Could be an unsolicited message, or response to a timed out command.
            logger.warning(f"Received packet with ID {packet_id}, but no matching pending command found.")

    def send_command(self,
                     command_id: int,
                     payload: bytes = b'',
                     callback: Optional[Callable[[int, int, bytes], None]] = None
                     ) -> int:
        """
        Encodes and sends a command and packet to the Arduino.
        Registers an optional callback to be called when a response 
        with matching packet ID is received.

        Args:
            command_id (int): The command ID.
            payload (bytes, optional): The payload. Defaults to empty.
            callback (Callable[int, int, bytes], optional) A function to call
                when a response with matching packet ID is received. The callback 
                will receive paramaters (packet_id: int, response_id: int, payload: bytes)

        Returns:
            int: The packet ID used for this command.

        Raises:
            ArduinoConnectionError: If not connected.
            ArduinoProtocolError: If payload size is invalid.
            ArduinoCommunicationError: For other serial communication errors.
        """
        if not self.is_connected():
            logger.error("Arduino not connected, cannot send command.")
            raise ArduinoConnectionError("Connection is not open or available.")

        packet_id = next(self._packet_id_generator)
        try:
            encoded_packet = arduino_protocol.encode_packet(packet_id, command_id, payload)
            with self._pending_commands_lock:
                self._pending_commands[packet_id] = {
                        'command_id': command_id,
                        'callback': callback,
                        'timestamp': time.time()
                        }
            logger.debug(f"Registered callback for packet {packet_id}.")
            self._connection.write(encoded_packet) # pyright: ignore[reportOptionalMemberAccess]
            logger.info(f"Sent command {command_id}, with packet ID {packet_id}.")
            return packet_id

        except ValueError as e:
            logger.error("Protocol error during packet encoding: {e}")
            raise ArduinoProtocolError("Packet encoding failed.") from e
        except serial.SerialException as e:
            with self._pending_commands_lock:
                self._pending_commands.pop(packet_id, None)
            logger.exception("Serial exception during send_command.")
            raise ArduinoCommunicationError("Serial communication failure during send_command.") from e
        except Exception as e:
            with self._pending_commands_lock:
                self._pending_commands.pop(packet_id, None)
            logger.exception("An unexpected error occured during send_command.")
            raise ArduinoCommunicationError("Unexpected error during send_command") from e

    def cleanup_pending_commands(self, timeout_seconds: float):
        """
        Removes pending commands that have been waiting longer than the specified
        timeout. Should be called in the main loop.
        """
        now = time.time()
        expired_packet_ids = []
        with self._pending_commands_lock:
            for packet_id, info in self._pending_commands.items():
                if now - info.get("timestamp", now) > timeout_seconds:
                    expired_packet_ids.append(packet_id)

            for packet_id in expired_packet_ids:
                logger.warning(f"Pending command for packet {packet_id} timed out.")
                self._pending_commands.pop(packet_id, None)


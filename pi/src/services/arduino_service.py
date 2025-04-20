from abc import ABC, abstractmethod
import logging
import time
from typing import Any, Optional

from serial import Serial, SerialException

logger = logging.getLogger(__name__)

class ArduinoCommunicationError(Exception):
    """Base class for errors related to Arduino communication."""

class ArduinoTimeoutError(ArduinoCommunicationError):
    """Raised when a communication timeout occurs."""

class ArduinoProtocolError(ArduinoCommunicationError):
    """Raised when there's an error related to the communication protocol."""

class ArduinoChecksumError(ArduinoProtocolError):
    """Raised when checksum mismatch occurs."""

class ArduinoPacketSizeError(ArduinoProtocolError):
    """Raised when packet size exceeds maximum."""

class ArduinoConnectionError(ArduinoCommunicationError):
    """Raised for issues related to serial connection state."""

class Protocol:
    START_BYTE = 0xAA
    MAX_BUFF_SIZE = 64
    T_UINT16 = 0x01
    T_UINT16_ARR = 0xA1

    @staticmethod
    def get_checksum(packet: bytearray | bytes) -> int:
        """
        Generates XOR checksum for input packet.

        Args:
            packet (bytearray): Packet to create a checksum for.

        Returns:
            int: Valid XOR checksum for the input packet.
        """
        checksum = 0
        for b in packet:
            checksum ^= b
        return checksum

class ArduinoCommand(ABC):
    """
    Base class for all Arduino commands, handling
    command IDs, encoding and parsing expected
    responses for this command type.
    """
    @abstractmethod
    def get_command_id(self) -> int:
        """Get the command ID, used for the packet header."""

    @abstractmethod
    def get_payload(self) -> bytes:
        """
        Get the command's binary payload, containing the 
        paramaters. Used as the packet body.
        """
    
    @abstractmethod
    def parse_response(self, response_type: int, response_packet: bytes) -> Any:
        """
        Parses the response packet recieved from the Arduino
        for this specific command. Handles the return values.

        Args:
            response_packet (bytes): The bytes recieved from the Arduino.
        """

    def encode(self) -> bytes:
        """
        Encodes the command into a complete binary packet,
        including the header and checksum. Packet will now
        be ready to send to the Arduino.

        Returns:
            bytes: Fully encoded packet. Ready to send to
                the Arduino.
        """
        command_id = self.get_command_id()
        payload = self.get_payload()

        header = bytes([Protocol.START_BYTE, command_id, len(payload)])
        packet = bytearray(header + payload)
        packet.append(Protocol.get_checksum(packet))
        return bytes(packet)

class ArduinoService:
    """
    Handles communication between the Arduino and the
    Raspberry Pi, using serial communication.
    """
    def __init__(self, port: str, baud_rate: int, timeout: float = 1):
        self._port = port
        self._baud_rate= baud_rate
        self._timeout = timeout
        self._connection: Optional[Serial] = None

    def connect(self) -> bool:
        """
        Open the serial connection with the Arduino.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            self._connection = Serial(
                    self._port, 
                    self._baud_rate,
                    timeout = self._timeout
                    )
            time.sleep(2)  # Wait for Arduino initialization.
                           # Handshake would be better.
            return True
        except SerialException:
            logger.error("ARDUINO: Could not connect. Check connection.")
            return False

    def disconnect(self):
        """Closes the serial connection."""
        if self._connection and self._connection.is_open:
            self._connection.close()
            self._connection = None
            logger.info("ARDUINO: Connection closed.")
        else:
            logger.info("ARDUINO: Attempting to close non-existant connection.")
    
    def _listen_for_packet_start(self):
        """
        Listens for a packet start, as defined by Protocol.START_BYTE.

        Raises:
            ArduinoTimeoutError: If the packet start is not found before timeout.
            ArduinoConnectionError: If the connection is unavailable.
            SerialException: If an underlying serial communication error occurs.
        """
        if not self._connection or not self._connection.is_open:
            raise ArduinoConnectionError("Connection is not open or available.")

        try:
            while True:
                start = self._connection.read(1)
                if not start:
                    logger.error("ARDUINO: Timeout waiting for packet start byte.")
                    raise ArduinoTimeoutError("Timeout waiting for packet start byte.")
                if start[0] == Protocol.START_BYTE:
                    return
        except SerialException:
            logger.exception("ARDUINO: Serial exception while listening for start byte.")
            raise

    def _read_header(self) -> tuple[int, int]:
        """
        Reads the packet header (Response Type, Payload Length)

        Returns:
            tuple[int, int]: Response Type, Payload Length

        Raises:
            ArduinoTimeoutError: If the header cannot be read before timeout.
            ArduinoConnectionError: If the connection is unavailable.
            SerialException: If an underlying serial communication error occurs.
        """
        if not self._connection or not self._connection.is_open:
            raise ArduinoConnectionError("Connection is not open or available.")
        
        try:
            header = self._connection.read(2)
            if len(header) < 2:
                logger.error("ARDUINO: Timeout waiting for response header.")
                raise ArduinoTimeoutError(f"Timeout while waiting for response header. Expected 2 bytes, recieved {len(header)}.")
            return (header[0], header[1])  # response_type, payload_length
        except SerialException:
            logger.exception("ARDUINO: Serial exception while reading response header.")
            raise
    
    def _read_payload(self, payload_length: int) -> bytes:
        """
        Reads the packet payload.

        Args:
            payload_length (int): Expected payload length.

        Returns:
            bytes: Binary payload.
        
        Raises:
            ArduinoTimeoutError: If the payload cannot be read before timeout.
            ArduinoPacketSizeError: If the declared payload length exceeds protocol maximum.
            ArduinoConnectionError: If the connection is unavailable.
            SerialException: If an underlying serial communication error occurs.
        """
        if not self._connection or not self._connection.is_open:
            raise ArduinoConnectionError("Connection is not open or available.")

        max_payload_length = Protocol.MAX_BUFF_SIZE - 3  # START_BYTE + HEADER
        if payload_length > max_payload_length:
            logger.error(f"ARDUINO: Declared payload length ({payload_length}) exceeds max allowed ({Protocol.MAX_BUFF_SIZE}).")
            raise ArduinoPacketSizeError(f"Declared payload length ({payload_length}) exceeds max allowed ({Protocol.MAX_BUFF_SIZE}).")

        if payload_length == 0:
            return b''
        try:
            payload = self._connection.read(payload_length)
            if len(payload) < payload_length:
                logger.error(f"ARDUINO: Timeout reading payload. Got {len(payload)} bytes, expected {payload_length}.")
                raise ArduinoTimeoutError(f"Timeout reading payload. Got {len(payload)} bytes, expected {payload_length}.")
            return payload
        except SerialException:
            logger.exception("ARDUINO: Serial exception while reading payload.")
            raise

    def _read_and_validate_checksum(self, packet: bytearray):
        """
        Reads the checksum byte, generates the expected checksum
        value for the input packet, and ensures they match.

        Args:
            packet (bytearray): A packet, without the checksum byte.

        Raises:
            ArduinoTimeoutError: If the checksum byte cannot be read before timeout.
            ArduinoChecksumError: If the recieved checksum does not match the expected.
            ArduinoConnectionError: If the connection is unavailable.
            SerialException: If an underlying serial communication error occurs.
        """
        if not self._connection or not self._connection.is_open:
            raise ArduinoConnectionError("Connection is not open or available.")
        
        try:
            checksum_byte = self._connection.read(1)[0]
            if not checksum_byte:
                logger.error("ARDUINO: Timeout waiting for checksum byte.")
                raise ArduinoTimeoutError("Timeout waiting for checksum byte.")

            expected_checksum = Protocol.get_checksum(packet)
            if expected_checksum != checksum_byte:
                logger.error("ARDUINO: Checksum mismatch.")
                raise ArduinoChecksumError("Checksum mismatch.")
        except SerialException:
            logger.exception("ARDUINO: Serial error while reading checksum.")
            raise

    def _read_response_packet(self, 
                              timeout: Optional[float] = None
                              ) -> tuple[int, bytes]:
        """
        Listen for and read a response packet. Handles timeouts
        and checksum validation.

        Args:
            timeout (Optional[float]): Optional custom timeout for this 
                operation, in seconds.

        Returns:
            tuple[int, bytes]: Response code, binary packet payload.

        Raises:
            ArduinoCommunicationError: For any communication or protocol errors.
            ArduinoConnectionError: If the connection is unavailable.
            SerialException: If an underlying serial communication error occurs.
        """
        if not self._connection or not self._connection.is_open:
            raise ArduinoConnectionError("Connection is not open or available.")

        original_timeout = self._connection.timeout
        if timeout is not None:
            self._connection.timeout = max(0, timeout)

        try:
            self._listen_for_packet_start()
            response_type, payload_length = self._read_header()
            payload = self._read_payload(payload_length)
            
            packet_for_checksum = bytearray([Protocol.START_BYTE, response_type, payload_length]) + payload
            self._read_and_validate_checksum(packet_for_checksum)
            return response_type, payload

        except (ArduinoCommunicationError, SerialException):
            logger.exception("ARDUINO: Exception reading response packet.")
            if self._connection and self._connection.is_open:
                self._connection.reset_input_buffer()
            raise

        finally:
            if timeout is not None and self._connection:
                self._connection.timeout = original_timeout
    
    def send(self, command: ArduinoCommand):
        """
        Sends a comamnd to the Arduino, does not wait for a response.

        Args:
            command (ArduinoCommand): The command to send.

        Raises:
            ArduinoConnectionError: If not connected.
            ArduinoCommunicationError: For any communication or protocol errors.
        """
        if not self._connection or not self._connection.is_open:
            logger.error("ARDUINO: Not connected. Cannot send command.")
            raise ArduinoConnectionError("Connection is not open or available.")

        try:
            packet = command.encode()
            self._connection.reset_input_buffer()
            self._connection.write(packet)
        except SerialException as e:
            logger.exception("ARDUINO: Serial exception during transmission.")
            raise ArduinoCommunicationError("Serial communication failure.") from e

    def send_and_await_response(self, 
                                command: ArduinoCommand, 
                                timeout: Optional[float] = None
                                ) -> Any:
        """
        Send a command to the Arduino and awaits the response.

        Args:
            command (ArduinoCommand): The command to send.
            timeout (Optional[Float]): Optional custom timeout for serial.

        Returns:
            tuple[int, bytes]: (Response Code, Response Binary Packet Payload)

        Raises:
            ArduinoConnectionError: If not connected.
            ArduinoCommunicationError: For any communication or protocol errors.
        """
        if not self._connection or not self._connection.is_open:
            logger.error("ARDUINO: Not connected. Cannot send comamnd.")
            raise ArduinoConnectionError("Connection is not open or available.")

        try:
            packet = command.encode()
            self._connection.reset_input_buffer()
            self._connection.write(packet)
            response = self._read_response_packet(timeout=timeout)
            return command.parse_response(*response)

        except ArduinoCommunicationError:
            logger.exception("ARDUINO: Protocol/communication error during send/recieve.")
            raise
        except SerialException as e:
            logger.exception("ARDUINO: Serial exception during transmission.")
            raise ArduinoCommunicationError("Serial communication failure.") from e


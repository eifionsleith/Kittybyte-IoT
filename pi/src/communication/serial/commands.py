import struct
from abc import ABC, abstractmethod 
from dataclasses import dataclass

from .protocol import Protocol

class ArduinoCommand(ABC):
    """Base class for all Arduino commands."""
    
    @staticmethod
    def _get_checksum(packet: bytearray):
        """Creates a checksum byte for the packet."""
        checksum = 0
        for b in packet:
            checksum ^= b 
        return checksum

    @abstractmethod 
    def get_command_id(self) -> int:
        """Get the command ID byte."""
        ...

    @abstractmethod 
    def get_payload(self) -> bytes:
        """Gets the binary payload for this command."""
        ...

    def encode(self) -> bytes:
        """Encode the command into a complete binary packet."""
        command_id = self.get_command_id()
        payload = self.get_payload()

        header = bytes([Protocol.START_BYTE, command_id, len(payload)])
        packet = bytearray(header + payload)
        packet.append(self._get_checksum(packet))
        return bytes(packet)
        

@dataclass
class DispenseCommand(ArduinoCommand):
    """Command to dispense a portion."""
    quantity: int = 1

    def __post_init__(self):
        if self.quantity < 1:
            raise ValueError("Dispense quantity must be at least 1")

    def get_command_id(self) -> int:
        return Protocol.CMD_DISPENSE

    def get_payload(self) -> bytes:
        return bytes([Protocol.TYPE_UINT16]) + struct.pack('<H', self.quantity)

@dataclass 
class BuzzCommand(ArduinoCommand):
    """Command to activate the buzzer."""
    duration_ms: int = 500
    frequency: int = 2000

    def __post_init__(self):
        if self.duration_ms < 1:
            raise ValueError("Duration must be positive.")
        if self.frequency < 1:
            raise ValueError("Frequency must be positive.")

    def get_command_id(self) -> int:
        return Protocol.CMD_BUZZ

    def get_payload(self) -> bytes:
        bytes_frequency = bytes([Protocol.TYPE_UINT16]) + struct.pack('<H', self.frequency)
        bytes_duration = bytes([Protocol.TYPE_UINT16]) + struct.pack('<H', self.duration_ms)
        return bytes_frequency + bytes_duration


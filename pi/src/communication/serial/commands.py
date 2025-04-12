from abc import ABC, abstractmethod 
from dataclasses import dataclass

class ArduinoCommand(ABC):
    """Base class for all Arduino commands."""
    
    @abstractmethod 
    def to_serial_string(self) -> str:
        """Convert the command to a string to send over serial."""
        ...

@dataclass
class DispenseCommand(ArduinoCommand):
    """Command to dispense a portion."""
    quantity: int = 1

    def __post_init__(self):
        if self.quantity < 1:
            raise ValueError("Dispense quantity must be at least 1")

    def to_serial_string(self) -> str:
        return f"dispense {self.quantity}"

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

    def to_serial_string(self) -> str:
        return f"buzz {self.duration_ms} {self.frequency}"


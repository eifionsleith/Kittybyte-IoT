import logging

logger = logging.getLogger(__name__)

# --- Protocol Constants ---
START_BYTE = 0xAA
MAX_BUFFER_SIZE = 64
MAX_PAYLOAD_SIZE = MAX_BUFFER_SIZE - 5

# --- Command IDs
CMD_BUZZER_SIMPLE = 0x10
CMD_BUZZER_MELODY = 0x11

# -- Response IDs 
R_NOTIFY_COMMAND_RECEIVED = 0xA0
R_NOTIFY_TASK_COMPLETE = 0xA1
R_ERROR_UNKNOWN_COMMAND = 0xE0
R_ERROR_INVALID_PAYLOAD = 0xE1
R_ERROR_RESOURCE_BUSY = 0xE2
R_ERROR_TASK_FAILED = 0xE3

def get_response_message(response_code: int) -> str:
    """
    Returns a human readable response message from 
    the response code (defined above).
    """
    response_codes = {
            R_NOTIFY_COMMAND_RECEIVED: "NOTIFY_COMMAND_RECEIVED",
            R_NOTIFY_TASK_COMPLETE: "NOTIFY_TASK_COMPLETE",
            R_ERROR_UNKNOWN_COMMAND: "ERROR_UNKNOWN_COMMAND",
            R_ERROR_INVALID_PAYLOAD: "ERROR_INVALID_PAYLOAD",
            R_ERROR_RESOURCE_BUSY: "ERROR_RESOURCE_BUSY",
            R_ERROR_TASK_FAILED: "ERROR_TASK_FAILED"
            }
    return response_codes.get(response_code, "UNKNOWN_RESPONSE")

def calculate_checksum(data_bytes: bytes) -> int:
    """
    Calculates an XOR checksum for the given bytes.
    """
    checksum = 0 
    for byte in data_bytes:
        checksum ^= byte
    return checksum

def encode_packet(packet_id: int, command_id: int, payload: bytes = b'') -> bytes:
    """
    Encodes a command packet according to the protocol.
    Format: [START_BYTE] [PACKET_ID] [COMMAND_ID] [PAYLOAD_LENGTH] [PAYLOAD] [CHECKSUM]

    Args:
        packet_id (int): Unique identifier for this packet (0-255).
        command_id (int): The ID of the command to execute (0-255).
        payload (bytes, optional): The payload data, defaults to empty bytes.

    Returns:
        bytes: The complete encoded packet ready to be sent.

    Raises:
        ValueError: If the payload size exceeds MAX_PAYLOAD_SIZE.
    """
    if len(payload) > MAX_PAYLOAD_SIZE:
        raise ValueError(f"Payload size ({len(payload)}) exceeds maximum allowed ({MAX_PAYLOAD_SIZE})")
    
    # Header: START_BYTE, PACKET_ID, COMMAND_ID, PAYLOAD_LENGTH
    header = bytes([START_BYTE, packet_id, command_id, len(payload)])
    data_for_checksum = header + payload
    checksum = calculate_checksum(data_for_checksum)

    full_packet = data_for_checksum + bytes([checksum])
    
    logger.debug(f"Encoded packet (ID: {packet_id}, CMD: {command_id}, PAY_L: {len(payload)}, CHECKSUM: {checksum}): {full_packet.hex()}")

    return full_packet


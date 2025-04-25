# Test script to send an invalid command ID with a specific packet ID
# and verify the response from the Arduino.

import serial
import struct
import time
import sys

# --- Protocol Constants ---
START_BYTE = 0xAA

# Command IDs (from Commands.h) - Included for reference, we'll send an invalid one
CMD_BUZZER_SIMPLE = 0x10
CMD_BUZZER_MELODY = 0x11

# Response IDs (from Commands.h)
RESP_NOTIFY_COMMAND_RECEIVED = 0xA0
RESP_NOTIFY_TASK_COMPLETE = 0xA1
RESP_ERROR_UNKNOWN_COMMAND = 0xE0
RESP_ERROR_INVALID_PAYLOAD = 0xE1
RESP_ERROR_RESOURCE_BUSY = 0xE2
RESP_ERROR_TASK_FAILED = 0xE3

# Map response IDs to human-readable names
RESPONSE_CODES = {
    RESP_NOTIFY_COMMAND_RECEIVED: "NOTIFY_COMMAND_RECEIVED",
    RESP_NOTIFY_TASK_COMPLETE: "NOTIFY_TASK_COMPLETE",
    RESP_ERROR_UNKNOWN_COMMAND: "ERROR_UNKNOWN_COMMAND",
    RESP_ERROR_INVALID_PAYLOAD: "ERROR_INVALID_PAYLOAD",
    RESP_ERROR_RESOURCE_BUSY: "ERROR_RESOURCE_BUSY",
    RESP_ERROR_TASK_FAILED: "ERROR_TASK_FAILED",
}

# --- Configuration ---
SERIAL_PORT = '/dev/ttyACM0'  # <-- CHANGE THIS to your Arduino's serial port
BAUD_RATE = 9600
READ_TIMEOUT_SECONDS = 2.0 # Timeout for waiting for a response packet

# --- Test Parameters ---
TEST_PACKET_ID = 234       # The specific packet ID to use for this test
INVALID_COMMAND_ID = 0xFF  # An arbitrary command ID that is not defined in Commands.h

# --- Helper Function ---
def calculate_checksum(data_bytes):
    """Calculates the XOR checksum for the given bytes."""
    checksum = 0
    for byte in data_bytes:
        checksum ^= byte
    return checksum

# --- Packet Reading Function (Modified to include packet_id) ---
def read_response_packet(ser, timeout):
    """
    Reads and parses a response packet from the serial port using a state machine.
    Assumes packet format: [START_BYTE] [PACKET_ID] [RESPONSE_ID] [PAYLOAD_LENGTH] [PAYLOAD (optional)] [CHECKSUM]
    Returns a dictionary with packet info if successful, None otherwise.
    """
    state = "WAITING_FOR_START"
    start_time = time.time()
    packet = {
        "packet_id": None,
        "response_id": None,
        "payload_length": 0,
        "payload": b'',
        "received_checksum": None,
        "calculated_checksum": None,
        "is_valid": False,
        "raw_bytes": bytearray()
    }
    payload_buffer = bytearray()
    bytes_received_count = 0
    # Max payload size from Protocol.h (MAX_BUFFER_SIZE=64 - 5 header bytes)
    MAX_PAYLOAD_SIZE = 59

    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            byte = ser.read(1)
            if not byte:
                continue

            current_byte = byte[0]
            packet["raw_bytes"].append(current_byte)

            if state == "WAITING_FOR_START":
                if current_byte == START_BYTE:
                    state = "READING_PACKET_ID"
                else:
                     packet["raw_bytes"].clear() # Discard bytes before start byte

            elif state == "READING_PACKET_ID":
                packet["packet_id"] = current_byte
                state = "READING_RESPONSE_ID"

            elif state == "READING_RESPONSE_ID":
                packet["response_id"] = current_byte
                state = "READING_LENGTH"

            elif state == "READING_LENGTH":
                if current_byte > MAX_PAYLOAD_SIZE:
                    # Invalid length, reset state machine
                    print(f"Warning: Received invalid payload length ({current_byte}). Resetting.")
                    state = "WAITING_FOR_START"
                    packet = {k: None if k != "raw_bytes" else bytearray() for k in packet} # Reset packet
                    payload_buffer.clear()
                    bytes_received_count = 0
                else:
                    packet["payload_length"] = current_byte
                    bytes_received_count = 0
                    payload_buffer.clear()
                    if packet["payload_length"] == 0:
                        state = "VALIDATING_CHECKSUM"
                    else:
                        state = "READING_PAYLOAD"

            elif state == "READING_PAYLOAD":
                payload_buffer.append(current_byte)
                bytes_received_count += 1
                if bytes_received_count == packet["payload_length"]:
                    packet["payload"] = bytes(payload_buffer)
                    state = "VALIDATING_CHECKSUM"

            elif state == "VALIDATING_CHECKSUM":
                packet["received_checksum"] = current_byte

                # Prepare data for checksum calculation: START_BYTE, PACKET_ID, RESPONSE_ID, PAYLOAD_LENGTH, PAYLOAD
                checksum_data = bytes([START_BYTE, packet["packet_id"], packet["response_id"], packet["payload_length"]]) + packet["payload"]
                packet["calculated_checksum"] = calculate_checksum(checksum_data)

                # Validate checksum
                if packet["calculated_checksum"] == packet["received_checksum"]:
                    packet["is_valid"] = True
                    return packet # Success! Return the valid packet
                else:
                    print(f"Warning: Checksum mismatch! Expected {packet['calculated_checksum']:#04x}, Got {packet['received_checksum']:#04x}. Discarding packet.")
                    state = "WAITING_FOR_START" # Reset and look for next packet
                    packet = {k: None if k != "raw_bytes" else bytearray() for k in packet} # Reset packet
                    payload_buffer.clear()
                    bytes_received_count = 0
        else:
            # No data available, wait briefly
            time.sleep(0.01)

    # Timeout occurred before a complete packet was received
    return None


# --- Main Logic ---
def send_invalid_command(port, baud, packet_id, invalid_command_id):
    """Constructs and sends an invalid command packet, then waits for a response."""

    # Packet format: [START_BYTE] [PACKET_ID] [COMMAND_ID] [PAYLOAD_LENGTH] [CHECKSUM]
    # For an invalid command, the payload length will likely be 0, but the Arduino
    # might send back the invalid command ID in the error response payload.
    # We'll send a command with 0 payload length.

    payload = bytes([]) # No payload for this invalid command test
    payload_length = len(payload)

    # Data for checksum: START_BYTE, PACKET_ID, COMMAND_ID, PAYLOAD_LENGTH, PAYLOAD
    packet_data = bytes([START_BYTE, packet_id, invalid_command_id, payload_length]) + payload
    checksum = calculate_checksum(packet_data)
    packet_to_send = packet_data + bytes([checksum])

    print("--- Sending Invalid Command ---")
    print(f"Serial Port: {port}")
    print(f"Packet ID: {packet_id}")
    print(f"Invalid Command ID: 0x{invalid_command_id:02x}")
    print(f"Packet to Send ({len(packet_to_send)} bytes): {packet_to_send.hex()}")

    ser = None
    try:
        ser = serial.Serial(port, baud, timeout=READ_TIMEOUT_SECONDS)
        print(f"\nSerial port {port} opened.")

        ser.reset_input_buffer()
        ser.write(packet_to_send)
        print("Command sent.")

        print("\n--- Waiting for Response ---")
        response = read_response_packet(ser, timeout=READ_TIMEOUT_SECONDS)

        if response:
            resp_id = response['response_id']
            resp_name = RESPONSE_CODES.get(resp_id, f"Unknown (0x{resp_id:02x})")
            validity = "VALID" if response['is_valid'] else "INVALID CHECKSUM"
            payload_hex = response['payload'].hex() if response['payload'] else "None"

            print("\n--- Received Response ---")
            print(f"Packet ID: {response['packet_id']}")
            print(f"Response ID: 0x{resp_id:02x} ({resp_name})")
            print(f"Payload Length: {response['payload_length']}")
            print(f"Payload: {payload_hex}")
            print(f"Status: {validity}")

            # Verification checks
            print("\n--- Verification ---")
            if response['is_valid']:
                print("Packet Checksum: PASSED")
                if response['packet_id'] == packet_id:
                    print(f"Packet ID Match ({packet_id}): PASSED")
                else:
                    print(f"Packet ID Match (Expected {packet_id}, Got {response['packet_id']}): FAILED")

                if resp_id == RESP_ERROR_UNKNOWN_COMMAND:
                    print(f"Response ID ({resp_name}): PASSED")
                    # Check if the payload contains the invalid command ID sent
                    if response['payload_length'] == 1 and response['payload'][0] == invalid_command_id:
                         print(f"Payload Content (Contains sent command ID 0x{invalid_command_id:02x}): PASSED")
                    else:
                         print(f"Payload Content (Expected 1 byte with 0x{invalid_command_id:02x}, Got {payload_hex}): FAILED")
                else:
                    print(f"Response ID (Expected ERROR_UNKNOWN_COMMAND, Got {resp_name}): FAILED")
            else:
                print("Packet Checksum: FAILED")

        else:
            print(f"No valid response packet received within {READ_TIMEOUT_SECONDS} seconds.")

    except serial.SerialException as e:
        print(f"\nError opening or communicating via serial port {port}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("\nSerial port closed.")


if __name__ == "__main__":
    port_arg = sys.argv[1] if len(sys.argv) > 1 else SERIAL_PORT
    send_invalid_command(port_arg, BAUD_RATE, TEST_PACKET_ID, INVALID_COMMAND_ID)

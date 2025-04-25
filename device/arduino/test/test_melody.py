# AI generated... be careful...
import serial
import struct
import time
import sys

# --- Protocol Constants ---
START_BYTE = 0xAA

# Command IDs (from Commands.h)
CMD_BUZZER_SIMPLE = 0x10
CMD_BUZZER_MELODY = 0x11 # Added Melody command ID

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
READ_TIMEOUT_SECONDS = 1.0 # Timeout for waiting for a response byte
MAX_PAYLOAD_SIZE = 61 # From Protocol.h (MAX_BUFFER_SIZE=64 - 3 header bytes)

# Melody parameters
MELODY_TEMPO = 120 # BPM
# Simple 8-note melody (frequencies in Hz)
# Using some common musical note frequencies (approximate)
MELODY_NOTES = [
    262, # C4
    294, # D4
    330, # E4
    349, # F4
    392, # G4
    440, # A4
    494, # B4
    523  # C5
]

# --- Helper Function ---
def calculate_checksum(data_bytes):
    """Calculates the XOR checksum for the given bytes."""
    checksum = 0
    for byte in data_bytes:
        checksum ^= byte
    return checksum

# --- Packet Reading Function (Copied from simple_buzz.py) ---
def read_response_packet(ser, timeout):
    """
    Reads and parses a response packet from the serial port using a state machine.
    Returns a dictionary with packet info if successful, None otherwise.
    """
    state = "WAITING_FOR_START"
    start_time = time.time()
    packet = {
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

    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            byte = ser.read(1)
            if not byte: # Should not happen if in_waiting > 0, but good practice
                continue

            current_byte = byte[0]
            packet["raw_bytes"].append(current_byte)
            # print(f"Debug: Read byte {current_byte:#04x} in state {state}") # Uncomment for detailed debug

            if state == "WAITING_FOR_START":
                if current_byte == START_BYTE:
                    state = "READING_RESPONSE_ID"
                else:
                     packet["raw_bytes"].clear() # Discard bytes before start byte

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

                # Prepare data for checksum calculation
                checksum_data = bytes([START_BYTE, packet["response_id"], packet["payload_length"]]) + packet["payload"]
                packet["calculated_checksum"] = calculate_checksum(checksum_data)

                # Validate checksum
                if packet["calculated_checksum"] == packet["received_checksum"]:
                    packet["is_valid"] = True
                    # print("Debug: Packet received and validated.") # Uncomment for detailed debug
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
    # print("Debug: Timeout while waiting for packet.") # Uncomment for detailed debug
    return None


# --- Main Logic ---
def send_melody_command(port, baud, tempo, notes):
    """Constructs BUZZER_MELODY command, sends it, and waits for responses."""

    notes_length = len(notes)
    # Payload: tempo (uint16_t BE), notes_length (byte), notes (uint16_t BE array)
    # Pack tempo (H for unsigned short, > for big-endian)
    payload = struct.pack('>H', tempo)
    # Pack notes_length (B for unsigned char)
    payload += struct.pack('B', notes_length)
    # Pack each note frequency (H for unsigned short, > for big-endian)
    for note in notes:
        payload += struct.pack('>H', note)

    payload_length = len(payload)

    if payload_length > MAX_PAYLOAD_SIZE:
        print(f"Error: Melody payload size ({payload_length}) exceeds max allowed ({MAX_PAYLOAD_SIZE}).")
        return

    packet_data = bytes([START_BYTE, CMD_BUZZER_MELODY, payload_length]) + payload
    checksum = calculate_checksum(packet_data)
    packet_to_send = packet_data + bytes([checksum])

    print("--- Sending Melody Command ---")
    print(f"Serial Port: {port}")
    print(f"Tempo: {tempo} BPM")
    print(f"Number of Notes: {notes_length}")
    print(f"Packet to Send ({len(packet_to_send)} bytes): {packet_to_send.hex()}")

    ser = None # Initialize ser to None
    try:
        ser = serial.Serial(port, baud, timeout=READ_TIMEOUT_SECONDS)
        print(f"\nSerial port {port} opened.")

        # Flush input buffer before sending (optional, good practice)
        ser.reset_input_buffer()

        # Send the packet
        ser.write(packet_to_send)
        print("Command sent.")

        print("\n--- Waiting for Responses ---")
        # Wait for responses. The melody duration depends on tempo and notes length.
        # A rough estimate: (60000 / tempo) * notes_length + some buffer
        estimated_duration_ms = (60000 / tempo) * notes_length
        overall_wait_time = (estimated_duration_ms / 1000.0) + 3.0 # Wait for estimated duration + 3 extra seconds
        end_wait_time = time.time() + overall_wait_time

        while time.time() < end_wait_time:
            response = read_response_packet(ser, timeout=0.1) # Short timeout for each read attempt
            if response:
                responses_received = [] # Initialize inside loop to collect responses per read_response_packet call
                responses_received.append(response)
                resp_id = response['response_id']
                resp_name = RESPONSE_CODES.get(resp_id, f"Unknown (0x{resp_id:02x})")
                validity = "VALID" if response['is_valid'] else "INVALID CHECKSUM"
                payload_hex = response['payload'].hex() if response['payload'] else "None"
                print(f"Received: ID=0x{resp_id:02x} ({resp_name}), Len={response['payload_length']}, Payload={payload_hex}, Status={validity}")
                # Optional: Break early if a specific response is received
                # if resp_id == RESP_NOTIFY_TASK_COMPLETE:
                #    break
            # If read_response_packet returns None, it means timeout for this attempt, continue waiting until overall timeout

        print(f"Finished waiting for responses (overall timeout: {overall_wait_time:.1f} seconds).")


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
    send_melody_command(port_arg, BAUD_RATE, MELODY_TEMPO, MELODY_NOTES)

#include "Protocol.h"
#include <Arduino.h>

namespace Protocol {
  enum class ParseState {
    WAITING_FOR_START,
    READING_COMMAND_ID,
    READING_LENGTH,
    READING_PAYLOAD,
    VALIDATING_CHECKSUM
  };

  static ParseState current_state = ParseState::WAITING_FOR_START;
  static byte recieved_command_id = 0;
  static byte expected_payload_length = 0;
  static byte payload_buffer[Protocol::MAX_PAYLOAD_SIZE];
  static byte bytes_recieved = 0;

  bool check_for_packet(ReceivedPacket& packet) {
    packet.reset();

    // While there are bytes in the buffer...
    while (Serial.available() > 0) {
      byte current_byte = Serial.read();

      switch(current_state) {
        case ParseState::WAITING_FOR_START:
          if (current_byte == START_BYTE) {
            current_state = ParseState::READING_COMMAND_ID;
          }
          break;

        case ParseState::READING_COMMAND_ID:
          recieved_command_id = current_byte;
          current_state = ParseState::READING_LENGTH;
          break;

        case ParseState::READING_LENGTH:
          // Packet must be malformed...
          if (current_byte > MAX_PAYLOAD_SIZE) {
            current_state = ParseState::WAITING_FOR_START;
          } else {
            expected_payload_length = current_byte;
            bytes_recieved = 0;
            // Can skip reading payload if there is none...
            if (expected_payload_length == 0){
              current_state = ParseState::VALIDATING_CHECKSUM;
            } else {
              current_state = ParseState::READING_PAYLOAD;
            }
          }
          break;

        case ParseState::READING_PAYLOAD:
          if (bytes_recieved < MAX_PAYLOAD_SIZE) {
            payload_buffer[bytes_recieved] = current_byte;
          }
          bytes_recieved++;

          if (bytes_recieved == expected_payload_length) {
            current_state = ParseState::VALIDATING_CHECKSUM;
          }
          break;

        case ParseState::VALIDATING_CHECKSUM:
          byte received_checksum = current_byte;

          byte checksum_data[MAX_BUFFER_SIZE];
          checksum_data[0] = START_BYTE;
          checksum_data[1] = recieved_command_id;
          checksum_data[2] = expected_payload_length;
          memcpy(&checksum_data[3], payload_buffer, expected_payload_length);
          
          byte calcualted_checksum = calculate_checksum(checksum_data, expected_payload_length + 3);

          if (calcualted_checksum == received_checksum) {
            packet.command_id = recieved_command_id;
            packet.payload_length = expected_payload_length;
            memcpy(packet.payload, payload_buffer, expected_payload_length);
            packet.is_valid = true;

            current_state = ParseState::WAITING_FOR_START;
            return true;
          } else {
            // Checksum failed, discard the malformed packet...
            current_state = ParseState::WAITING_FOR_START;
            return false;
          }
          break;
      }
    }

    // Not enough bytes to complete packet in buffer... maintain state for next call...
    return false;
  }

  byte calculate_checksum(const byte* data, byte length) {
    byte checksum = 0;
    for (byte i = 0; i < length; ++i) {
      checksum ^= data[i];
    }
    return checksum;
  }
  
  bool send_response(byte response_id, const byte* payload, byte payload_length) {
    if (payload_length > MAX_PAYLOAD_SIZE) {
      return false;  // Payload is too large to send...
    }                // Might be worth adding error handling?

    byte packet_buffer[MAX_BUFFER_SIZE];
    byte packet_length = 0;

    // Assemble the header...
    packet_buffer[0] = START_BYTE;
    packet_buffer[1] = response_id;
    packet_buffer[2] = payload_length;
    packet_length = 3;

    // memcpy the payload only if it exists...
    if (payload != nullptr && payload_length > 0) {
      memcpy(&packet_buffer[packet_length], payload, payload_length);
      packet_length += payload_length;
    }

    // Append the checksum...
    byte checksum = calculate_checksum(packet_buffer, packet_length);
    packet_buffer[packet_length] = checksum;
    packet_length += 1;

    Serial.write(packet_buffer, packet_length);
  }
}

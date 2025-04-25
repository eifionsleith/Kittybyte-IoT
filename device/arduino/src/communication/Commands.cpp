#include "Commands.h"
#include "Protocol.h"
#include "../actuators/BuzzerController.h"
#include <Arduino.h>

namespace Commands {
  namespace {
    /**
     * Reads a uint16_t value from a byte array in Big-Endian format.
     * (!) UNSAFE: Does not handle bound checks.
     *             It is your responsibility to ensure index + 1 is within bounds.
     */
    uint16_t read_uint16_big_endian(const byte* buffer, byte index) {
      return (uint16_t)(buffer[index] << 8 | buffer[index + 1]);
    }
  }

  void handle_command(const Protocol::ReceivedPacket& packet) {
    switch (packet.command_id) {
      case BUZZER_SIMPLE:
        handle_buzzer_simple(packet);
        break;
      case BUZZER_MELODY:
        handle_buzzer_melody(packet);
        break;
      default:
        byte error_payload[] = { packet.command_id };
        Protocol::send_response(packet.packet_id, ERROR_UNKNOWN_COMMAND, error_payload, sizeof(error_payload));
        break;
    }
  }

  void handle_buzzer_simple(const Protocol::ReceivedPacket& packet) {
    // --- PAYLOAD STRUCTURE ---
    // byte 0-1 : frequency (uint16_t, Big-Endian)
    // byte 2-3 : duration_ms (uint16_t, Big-Endian)
    
    const byte EXPECTED_LENGTH = 4;
    if (packet.payload_length != EXPECTED_LENGTH) {
      Protocol::send_response(packet.packet_id, ERROR_INVALID_PAYLOAD, nullptr, 0);
      return;
    }

    // Interpret paramaters as big-endian...
    uint16_t frequency = read_uint16_big_endian(packet.payload, 0);
    uint16_t duration_ms = read_uint16_big_endian(packet.payload, 2);

    if (frequency == 0 || duration_ms == 0) {
      Protocol::send_response(packet.packet_id, ERROR_INVALID_PAYLOAD, nullptr, 0);
      return;
    }
    
    if (!BuzzerController::start_simple_buzz(packet.packet_id, frequency, duration_ms)) {
      Protocol::send_response(packet.packet_id, ERROR_RESOURCE_BUSY, nullptr, 0);
      return;
    }

    Protocol::send_response(packet.packet_id, NOTIFY_COMMAND_RECEIVED, nullptr, 0);
  }

  void handle_buzzer_melody(const Protocol::ReceivedPacket& packet) {
    // --- PAYLOAD STRUCTURE ---
    // byte 0-1  : tempo (uint16_t, Big-Endian)
    // byte 2    : notes_array_length (byte)
    // byte 3..  : notes_array (uint16_t, Big-Endian)
    
    // --- VALIDATION ---
    // Packet must contain first three bytes to parse length...
    const byte MIN_EXPECTED_LENGTH = 3;
    if (packet.payload_length < MIN_EXPECTED_LENGTH) {
      Protocol::send_response(packet.packet_id, ERROR_INVALID_PAYLOAD, nullptr, 0);
      return;
    }

    // --- PARSING ---
    uint16_t tempo = read_uint16_big_endian(packet.payload, 0);
    byte notes_array_length = packet.payload[2];

    // Check if the full length matches the provided array length, acting as bounds check...
    // Playing a zero-length melody makes no sense...
    // Tempo of zero makes no sense either...
    byte expected_total_length = MIN_EXPECTED_LENGTH + (notes_array_length * 2);
    if (packet.payload_length != expected_total_length ||
        notes_array_length == 0 ||
        tempo == 0) {
      Protocol::send_response(packet.packet_id, ERROR_INVALID_PAYLOAD, nullptr, 0);
      return;
    }

    // Parse the array, one uint16_t at a time...
    uint16_t melody_notes[notes_array_length];
    for (byte i = 0; i < notes_array_length; ++i) {
      byte current_note_index_in_payload = MIN_EXPECTED_LENGTH + (i * sizeof(uint16_t));
      melody_notes[i] = read_uint16_big_endian(packet.payload, current_note_index_in_payload);
    }

    // Start the melody, returns false if pin isn't initiated or buzzer is busy...
    if (!BuzzerController::start_melody(packet.packet_id, tempo, melody_notes, notes_array_length)) {
      Protocol::send_response(packet.packet_id, ERROR_RESOURCE_BUSY, nullptr, 0);
      return;
    }

    Protocol::send_response(packet.packet_id, NOTIFY_COMMAND_RECEIVED, nullptr, 0);
  }
}


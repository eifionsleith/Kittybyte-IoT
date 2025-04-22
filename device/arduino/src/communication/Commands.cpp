#include "Commands.h"
#include "Protocol.h"
#include "../actuators/BuzzerController.h"
#include <Arduino.h>

namespace Commands {
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
        Protocol::send_response(ERROR_UNKNOWN_COMMAND, error_payload, sizeof(error_payload));
        break;
    }
  }

  void handle_buzzer_simple(const Protocol::ReceivedPacket& packet) {
    const byte EXPECTED_LENGTH = 4;
    if (packet.payload_length != EXPECTED_LENGTH) {
      Protocol::send_response(ERROR_INVALID_PAYLOAD, nullptr, 0);
      return;
    }

    uint16_t frequency = (packet.payload[0] << 8) | packet.payload[1];
    uint16_t duration_ms = (packet.payload[2] << 8) | packet.payload[3];

    if (frequency == 0 || duration_ms == 0) {
      Protocol::send_response(ERROR_INVALID_PAYLOAD, nullptr, 0);
      return;
    }
    
    if (!BuzzerController::start_simple_buzz(frequency, duration_ms)) {
      Protocol::send_response(ERROR_RESOURCE_BUSY, nullptr, 0);
      return;
    }

    Protocol::send_response(NOTIFY_COMMAND_RECEIVED, nullptr, 0);
  }

  void handle_buzzer_melody(const Protocol::ReceivedPacket& packet) {
    // TODO: This.
    Protocol::send_response(NOTIFY_COMMAND_RECEIVED, nullptr, 0);
  }
}


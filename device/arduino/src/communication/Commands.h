#pragma once
#include <Arduino.h>
#include "Protocol.h"

namespace Commands {
  // Command IDs, sent from the Pi
  const byte BUZZER_SIMPLE = 0x10;
  const byte BUZZER_MELODY = 0x11;
  // Response IDs, sent to the Pi 
  const byte NOTIFY_COMMAND_RECEIVED = 0xA0;
  const byte NOTIFY_TASK_COMPLETE = 0xA1;
  const byte ERROR_UNKNOWN_COMMAND = 0xE0;
  const byte ERROR_INVALID_PAYLOAD = 0xE1;
  const byte ERROR_RESOURCE_BUSY = 0xE2;
  const byte ERROR_TASK_FAILED = 0xE3;
  
  void handle_command(const Protocol::ReceivedPacket& packet);
  void handle_buzzer_simple(const Protocol::ReceivedPacket& packet);
  void handle_buzzer_melody(const Protocol::ReceivedPacket& packet);
}

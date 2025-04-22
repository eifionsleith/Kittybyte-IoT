#include "BuzzerController.h"
#include "../communication/Commands.h"
#include "../communication/Protocol.h"

namespace BuzzerController {
  namespace {
    BuzzerState current_state = BuzzerState::IDLE;
    unsigned long task_end_time = 0;
    const uint16_t* current_melody_notes = nullptr;
    const uint16_t current_melody_index = 0;
    byte buzzer_pin = -1;
  }

  void init(byte buzzer_pin_to_set) {
    buzzer_pin = buzzer_pin_to_set;
    pinMode(buzzer_pin, OUTPUT);
    digitalWrite(buzzer_pin, LOW);
    current_state = BuzzerState::IDLE;
  }

  void update() {
    if (current_state == BuzzerState::IDLE || buzzer_pin == (byte)-1) {
      return;
    }

    unsigned long now = millis();
    if (now >= task_end_time) {
      switch (current_state) {
        case BuzzerState::SIMPLE_DURATION:
          noTone(buzzer_pin);
          current_state = BuzzerState::IDLE;
          Protocol::send_response(Commands::NOTIFY_TASK_COMPLETE, nullptr, 0);
          break;
        case BuzzerState::PLAYING_MELODY:
          break;
        default:
          break;
      }
    }
  }

  bool start_simple_buzz(uint16_t frequency, uint16_t duration_ms) {
    if (current_state != BuzzerState::IDLE || buzzer_pin == (byte)-1) {
      return false;
    }

    current_state = BuzzerState::SIMPLE_DURATION;
    task_end_time = millis() + duration_ms;
    tone(buzzer_pin, frequency);
    return true;
  }
}

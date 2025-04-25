#include "BuzzerController.h"
#include "../communication/Commands.h"
#include "../communication/Protocol.h"

namespace BuzzerController {
  namespace {
    // True max size within the packet would be 29.
    // If packet size or structure changes this would need updating.
    const byte MAX_MELODY_NOTES = 30;

    struct CurrentMelody {
      uint16_t frequencies[MAX_MELODY_NOTES];
      uint16_t note_duration = 0;
      byte length = 0;
      byte current_frequency_index = 0;
    };

    byte buzzer_pin = -1;
    BuzzerState current_state = BuzzerState::IDLE;
    unsigned long task_end_time = 0;

    CurrentMelody active_melody;

    // Functions to handle each state, called each cycle by update(), based on current state.
    void handle_simple_buzz_state() {
      unsigned long now = millis();
      if (now > task_end_time) {
        noTone(buzzer_pin);
        current_state = BuzzerState::IDLE;
        Protocol::send_response(Commands::NOTIFY_TASK_COMPLETE, nullptr, 0);
      }
    }

    void handle_playing_melody_state() {
      unsigned long now = millis();
      if (now > task_end_time) {
        noTone(buzzer_pin);
        active_melody.current_frequency_index++;

        if (active_melody.current_frequency_index < active_melody.length) {
          tone(buzzer_pin, active_melody.frequencies[active_melody.current_frequency_index]);
          task_end_time = millis() + active_melody.note_duration;
        } else {
          current_state = BuzzerState::IDLE;
          Protocol::send_response(Commands::NOTIFY_TASK_COMPLETE, nullptr, 0);
        }
      }
    }
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

    switch (current_state) {
      case BuzzerState::SIMPLE_DURATION:
        noTone(buzzer_pin);
        current_state = BuzzerState::IDLE;
        Protocol::send_response(Commands::NOTIFY_TASK_COMPLETE, nullptr, 0);
        break;
      case BuzzerState::PLAYING_MELODY:
        handle_playing_melody_state();
        break;
      default:
        break;
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

  bool start_melody(uint16_t tempo, const uint16_t* frequencies, byte frequencies_l) {
    if (current_state != BuzzerState::IDLE || buzzer_pin == (byte) -1) {
      return false;
    }

    memcpy(active_melody.frequencies, frequencies, frequencies_l * sizeof(uint16_t));
    active_melody.length = frequencies_l;
    active_melody.current_frequency_index = 0;
    active_melody.note_duration = 60000 / tempo;
    
    current_state = BuzzerState::PLAYING_MELODY;
    tone(buzzer_pin, active_melody.frequencies[0]);
    task_end_time = millis() + active_melody.note_duration;

    return true;
  }
}

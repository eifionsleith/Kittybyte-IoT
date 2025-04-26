#pragma once
#include <Arduino.h>

namespace BuzzerController {
  enum class BuzzerState {
    IDLE,
    SIMPLE_DURATION,
    PLAYING_MELODY
  };
  
  // Call once from setup()
  void init (byte buzzer_pin_to_set);
  
  // Call each main loop, handles timing of sounds.
  void update();

  // Sets the state to indicate a simple buzz should start
  bool start_simple_buzz(const byte packet_id, uint16_t frequency, uint16_t duration_ms);

  // Sets the state to indicate the start of a melody
  bool start_melody(const byte packet_id, const uint16_t tempo, const uint16_t* frequencies, const byte frequencies_l);

  // Returns the state - good for checking if IDLE, and therefore ready to recieve commands
  BuzzerState get_current_state();
}

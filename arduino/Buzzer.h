#pragma once
#include <Arduino.h>

class Buzzer {
  private:
    int pin;

  public:
    Buzzer(int buzzerPin);
    void begin();
    void playTone(int frequency, int duration_ms);
};

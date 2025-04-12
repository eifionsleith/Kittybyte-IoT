#include "Buzzer.h"

Buzzer::Buzzer(int buzzerPin) : pin(buzzerPin) {}

void Buzzer::begin() {
  pinMode(pin, OUTPUT);
  digitalWrite(pin, LOW);
}

void Buzzer::playTone(int frequency, int duration_ms) {
  for (long i = 0; i < duration_ms * 1000L; i += frequency * 2) {
    digitalWrite(pin, HIGH);
    delayMicroseconds(frequency);
    digitalWrite(pin, LOW);
    delayMicroseconds(frequency);
  }
}

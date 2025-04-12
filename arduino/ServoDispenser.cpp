#include "ServoDispenser.h"

constexpr int g_MinimumPosition = 0;
constexpr int g_MaximumPosition = 180;

ServoDispenser::ServoDispenser(int servoPin) : pin(servoPin) {}

void ServoDispenser::begin() {
  servo.attach(pin);
  servo.write(g_MinimumPosition);
}

void ServoDispenser::dispense(int quantity) {
  // Placeholder Dispensing Logic
  for (int i = 0; i < quantity; ++i) {
    servo.write(g_MaximumPosition);
    delay(1000);
    servo.write(g_MinimumPosition);
    delay(1000);
  }
  Serial.println("Dispense action completed");
}

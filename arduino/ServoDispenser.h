#pragma once
#include <Arduino.h>
#include <Servo.h>

class ServoDispenser {
private:
  Servo servo;
  int pin;

public:
  ServoDispenser(int servoPin);
  void begin();
  void dispense(int quantity);
};

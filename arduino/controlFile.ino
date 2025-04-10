#include <Servo.h>

Servo myservo;
const int servoPin = 5;
const int buzzerPin = 4;

void setup() {
  myservo.attach(servoPin);
  myservo.write(0);

  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW); // buzzer off

  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {

    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equalsIgnoreCase("dispense")) {
      triggerServo();
    } else if (command.equalsIgnoreCase("buzz")) {
      triggerBuzzer();
    } else {
      Serial.println("Unknown command");
    }
  }
}

void triggerServo() {
  myservo.write(180);
  delay(3000);
  myservo.write(0);
  Serial.println("Dispense action completed");
}

void triggerBuzzer() {
  digitalWrite(buzzerPin, 1000);
  delay(1000);
  digitalWrite(buzzerPin, LOW);
  Serial.println("Buzzer completed");
}

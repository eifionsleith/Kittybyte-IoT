#include <Servo.h>

Servo myservo;
constexpr int servoPin = 5;
constexpr int buzzerPin = 1;


void triggerServo() {
  myservo.write(1);
  delay(3000);
  myservo.write(180);
  Serial.println("Dispense action completed");
}

void f_PlayTone(int tone, int duration) {
  for (long i = 0; i < duration * 1000L; i+= tone * 2) {
    digitalWrite(buzzerPin, HIGH);
    delayMicroseconds(tone);
    digitalWrite(buzzerPin, LOW);
    delayMicroseconds(tone);
  }
}

void triggerBuzzer() {
  /* Play a little song */
  constexpr int notes[] = { 261, 329, 523, 493, 392 };
  for (int i = 0; i < 5; ++i) {
    f_PlayTone(notes[i], 200);
  }

  Serial.println("Buzzer completed");
}

void setup() {
  myservo.attach(servoPin);
  myservo.write(180);

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


#include "src/communication/Protocol.h"
#include "src/communication/Commands.h"
#include "src/actuators/BuzzerController.h"
#define BUZZER_PIN 6

void setup() {
  Serial.begin(115200);
  BuzzerController::init(BUZZER_PIN);
  while (!Serial);
}

void loop() {
  Protocol::ReceivedPacket incoming_packet;

  if (Protocol::check_for_packet(incoming_packet)) {
    if (incoming_packet.is_valid) {
      Commands::handle_command(incoming_packet);
    }
  }

  // Update all controllers.
  BuzzerController::update();
}

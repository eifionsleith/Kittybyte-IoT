#include "Serial.h"
#include "Buzzer.h"
#include "ServoDispenser.h"
#define MSG_OK 0x06
#define CMD_BUZZ 0xA1
#define CMD_DISPENSE 0xA3
#define TYPE_UINT16 0x01

#define SERVO_PIN 5
#define BUZZER_PIN 6

PacketBuffer gPacketBuffer;
ServoDispenser gDispenser(SERVO_PIN);
Buzzer gBuzzer(BUZZER_PIN);

uint16_t fnExtractUint16(byte* payload, byte& payloadIndex, bool* success) {
  if (payload[payloadIndex] != TYPE_UINT16) {
    *success = false;
    return 0;
  }
  payloadIndex++;

  uint16_t lowByte = payload[payloadIndex++];
  uint16_t highByte = payload[payloadIndex++];
  uint16_t result = (highByte << 8) | lowByte;

  if (success) *success = true;
  return result;
}

bool fnExecuteCommand(PacketBuffer* pb) {
  byte commandID = pb->ayBuffer[1];
  byte* payload = &(pb->ayBuffer[3]);
  byte payloadIndex = 0;

  switch (commandID) {
    case CMD_BUZZ: {
                     bool success;
                     uint16_t frequency = fnExtractUint16(payload, payloadIndex, &success);
                     if (!success) break;

                     uint16_t duration = fnExtractUint16(payload, payloadIndex, &success);
                     if (!success) break;

                     gBuzzer.playTone(frequency, duration);
                     return true;
                   }
    case CMD_DISPENSE: {
                         bool success;
                         uint16_t param = fnExtractUint16(payload, payloadIndex, &success);
                         if (!success) break;

                         gDispenser.dispense(param);
                         return true;
                       }
    default:
                       return false;
  }
}

void setup() {
  fnInitPacketBuffer(&gPacketBuffer);
  gDispenser.begin();
  gBuzzer.begin();
  Serial.begin(9600);
}

void loop() {
  if (fnRecievePacket(&gPacketBuffer)) {
    bool success = fnExecuteCommand(&gPacketBuffer);
    if (success) Serial.write(MSG_OK);
  }
}

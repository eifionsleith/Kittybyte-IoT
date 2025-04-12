#include "Serial.h"
#include "Buzzer.h"
#define MSG_OK 0x06
#define CMD_BUZZ 0xA1
#define TYPE_UINT16 0x01

#define BUZZER_PIN 6

PacketBuffer gPacketBuffer;
Buzzer gBuzzer(BUZZER_PIN);

void fnExecuteCommand(PacketBuffer* pb) {
  byte commandID = pb->ayBuffer[1];
  byte* payload = &(pb->ayBuffer[3]);
  byte payloadIndex = 0;

  switch (commandID) {
    case CMD_BUZZ: {
                     if (payload[payloadIndex++] == TYPE_UINT16) {
                       uint16_t frequency = *((uint16_t*)(payload + payloadIndex));
                       payloadIndex += 1 + sizeof(uint16_t);
                       uint16_t duration = *((uint16_t*)(payload + payloadIndex));
                       payloadIndex += 1 + sizeof(uint16_t);

                       gBuzzer.playTone(frequency, duration);
                     }
                     break;
                   }
  }
}

void setup() {
  fnInitPacketBuffer(&gPacketBuffer);
  gBuzzer.begin();
  Serial.begin(9600);
}

void loop() {
  if (fnRecievePacket(&gPacketBuffer)) {
    Serial.write(MSG_OK);
    fnExecuteCommand(&gPacketBuffer);
    // Acknowledge successful packet read.
  }
}

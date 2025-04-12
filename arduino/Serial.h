#define MAX_BUFFER_SIZE 64
#define START_BYTE 0xAA

typedef struct {
  byte ayBuffer[MAX_BUFFER_SIZE];
  byte yIndex;
  byte yExpectedLength;
  bool bRecievingPacket;
} PacketBuffer;

void fnInitPacketBuffer(PacketBuffer* pb) {
  pb -> yIndex = 0;
  pb -> yExpectedLength = 0;
  pb -> bRecievingPacket = false;
}

bool fnValidateChecksum(PacketBuffer* pb) {
  byte yChecksum = 0;
  for (byte i = 0; i < pb -> yIndex - 1; i++) {
    yChecksum ^= pb->ayBuffer[i];
  }
  return yChecksum == pb->ayBuffer[pb->yIndex - 1];
}

bool fnRecievePacket(PacketBuffer* pb) {
  while (Serial.available()) {
    byte b = Serial.read();

    if (!pb->bRecievingPacket) {
      if (b == START_BYTE) {
        // New packet.
        pb->bRecievingPacket = true;
        pb->yIndex = 0;
        pb->ayBuffer[pb->yIndex++] = b;
      }
    } 
    // Ignore non-start bytes when not receiving
    else {
      // Continue existing packet.
      pb->ayBuffer[pb->yIndex++] = b;

      // len byte 
      if (pb->yIndex == 3) {
        pb->yExpectedLength = b;
      }

      // Full packet received
      if (pb->yIndex >= 3 + pb->yExpectedLength + 1) {
        pb->bRecievingPacket = false;
        return fnValidateChecksum(pb);
      }

      // Buffer overflow protection
      if (pb->yIndex >= MAX_BUFFER_SIZE) {
        pb->bRecievingPacket = false;
      }
    }
  }
  return false;
}

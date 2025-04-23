// src/communication/Protocol.h
#pragma once
#include <Arduino.h>


namespace Protocol {
  const byte START_BYTE = 0xAA;
  const byte MAX_BUFFER_SIZE = 64;
  const byte MAX_PAYLOAD_SIZE = MAX_BUFFER_SIZE - 4; // 4 = 1 START_BYTE + 1 COMMAND_ID + 1 PAYLOAD_LENGTH + 1 CHECKSUM 
  
  /** Structure representing a packet as recieved by the protocol */
  struct ReceivedPacket {
    byte command_id = 0;
    byte payload[Protocol::MAX_BUFFER_SIZE];
    byte payload_length = 0;
    bool is_valid = false;

    void reset() {
      command_id = 0;
      payload_length = 0;
      is_valid = false;
    }
  };

  bool check_for_packet(ReceivedPacket& packet);
  byte calculate_checksum(const byte* data, byte length);
  bool send_response(byte response_id, const byte* payload, byte payload_length);
}

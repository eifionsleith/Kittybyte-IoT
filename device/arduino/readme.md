# Arduino Serial Control for Raspberry Pi
## Communication Protocol

Communication relies on a simple packet structure sent over the serial connection.

* **Packet Format:**
    ```
    [START_BYTE] [PACKET_ID] [COMMAND_ID/RESPONSE_ID] [PAYLOAD_LENGTH] [PAYLOAD (optional)] [CHECKSUM]
    ```
* **`START_BYTE`:** Always `0xAA`.
* **`PACKET_ID`:** A single byte used to associate responses with commands.
* **`COMMAND_ID` / `RESPONSE_ID`:** A single byte identifying the command or response (see Commands and Responses below).
* **`PAYLOAD_LENGTH`:** A single byte indicating the length of the `PAYLOAD` in bytes (0 if no payload). Maximum payload size is 59 bytes (`MAX_PAYLOAD_SIZE`).
* **`PAYLOAD`:** Optional data associated with the command or response.
* **`CHECKSUM`:** A single byte calculated by XORing all preceding bytes in the packet (from `START_BYTE` to the end of the `PAYLOAD`).

### Commands (Pi -> Arduino)

* **`BUZZER_SIMPLE` (ID: `0x10`)**
    * Description: Activates the buzzer for a specific frequency and duration.
    * Payload (4 bytes):
        * Bytes 0-1: Frequency (uint16_t, Big-Endian)
        * Bytes 2-3: Duration (uint16_t, milliseconds, Big-Endian)
    * Example Payload (3000 Hz, 1000 ms): `0x0B 0xB8 0x03 0xE8` (Demonstrated in `simple_buzz.py`)
* **`BUZZER_MELODY` (ID: `0x11`)**
    * Description: Plays a sequence of notes.
    * Payload:
        * Bytes 0-1: Tempo (uint16_t, Big-Endian)
        * Byte 2: Number of notes (`notes_array_length`, byte)
        * Bytes 3 onwards: Notes array (sequence of uint16_t frequencies, Big-Endian)
    * The total payload length should be 3 + (`notes_array_length` * 2) bytes.
    * Demonstrated in `test_melody.py`.

### Responses (Arduino -> Pi)

The Arduino sends response packets back to the Pi using the same packet structure (START_BYTE, PACKET_ID, RESPONSE_ID, PAYLOAD_LENGTH, PAYLOAD, CHECKSUM).

* **`NOTIFY_COMMAND_RECEIVED` (ID: `0xA0`)**: Sent when a valid command is received and initiated.
* **`NOTIFY_TASK_COMPLETE` (ID: `0xA1`)**: Sent when a time-based task (like `BUZZER_SIMPLE` or `BUZZER_MELODY`) finishes.
* **`ERROR_UNKNOWN_COMMAND` (ID: `0xE0`)**: Sent if the received `COMMAND_ID` is not recognized. Payload contains the unrecognized command ID.
* **`ERROR_INVALID_PAYLOAD` (ID: `0xE1`)**: Sent if the payload length or content is incorrect for the command.
* **`ERROR_RESOURCE_BUSY` (ID: `0xE2`)**: Sent if a command cannot be executed because the resource (e.g., buzzer) is already in use.
* **`ERROR_TASK_FAILED` (ID: `0xE3`)**: Sent if a task fails unexpectedly (not currently used).

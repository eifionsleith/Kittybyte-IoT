import logging
import time
import struct
from communication.arduino_service import ArduinoService

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

def example_callback(packet_id: int, response_id: int, payload: bytes):
    logger.info(f"Callback triggered for packet_id: {packet_id}")
    

arduino_service = ArduinoService("/dev/ttyACM0", 9600)
arduino_service.connect()

# Define frequency (e.g., 1000 Hz) and duration (e.g., 500 ms)
frequency = 1000
duration_ms = 500

# Pack the frequency and duration into a payload (uint16_t, Big-Endian)
# Use '>H' for unsigned short (uint16_t) and Big-Endian byte order
payload = struct.pack('>HH', frequency, duration_ms)

arduino_service.send_command(0x10, payload=payload, callback=example_callback)

while True:
    arduino_service.process_incoming_data()
    arduino_service.cleanup_pending_commands(1)
    time.sleep(0.01)


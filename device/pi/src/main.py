import logging
import time
from communication.arduino_service import ArduinoService
from communication.commands.buzzer_commands import MelodyCommand

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)

def example_callback(packet_id: int, response_id: int, payload: bytes):
    logger.info(f"Callback triggered for packet_id: {packet_id}, response_id: {response_id}, payload: {payload.hex()}")
    

arduino_service = ArduinoService("/dev/ttyACM0", 9600)
arduino_service.connect()

cmd = MelodyCommand(120, [1000, 1200, 1400, 1000, 1200, 1400])

arduino_service.send_command(cmd.get_command_id(), payload=cmd.get_payload(), callback=example_callback)

while True:
    arduino_service.process_incoming_data()
    arduino_service.cleanup_pending_commands(10)
    time.sleep(0.01)


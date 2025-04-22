import time
from services.mqtt_service import MQTTService
from core.rpc_handlers import process_rpc_command
from communication.serial.arduino_controller import ArduinoController


def mqtt_example():
    mqtt_client = MQTTService("192.168.0.17", 1883, "mi79zwGei1yakoM5F1OM")
    mqtt_client.connect()
    arduino_controller = ArduinoController("/dev/ttyACM0", timeout=10)
    arduino_controller.connect()

    while True:
        rpc_command = mqtt_client.get_rpc_command()
        if rpc_command:
            result = process_rpc_command(rpc_command, arduino_controller)
            mqtt_client.send_rpc_response(rpc_command, "OK")

        time.sleep(1)


mqtt_example()


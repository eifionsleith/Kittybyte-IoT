import time
from communication.mqtt.mqtt_client import MQTTClient


def mqtt_example():
    mqtt_client = MQTTClient("localhost",
                             1883,
                             "SxpVEeiEaTXZNaEMDJov")
    mqtt_client.connect()
    time.sleep(10)


mqtt_example()


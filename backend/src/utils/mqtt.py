import paho.mqtt.publish as publish
from utils.settings import get_settings

def publish_single(topic: str, payload: str) -> None:
    broker_address = get_settings().mqtt_broker_address
    publish.single(topic, payload, hostname=broker_address)


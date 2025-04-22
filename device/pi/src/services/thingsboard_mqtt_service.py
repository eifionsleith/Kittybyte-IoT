import json
import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class ThingsboardMQTTService:
    """
    Handles MQTT communication between the device
    and Thingsboard.
    """
    def __init__(self, host: str, port: int, token: str, rpc_map):
        """
        Initializes the ThingsboardMQTTService.

        Args:
            host (str): Thingsboard host, e.g. thingsboard.cs.cf.ac.uk.
            port (str): Thingsboard MQTT port, e.g. 1833.
            token (str): Thingsboard access token, generated during provisioning.
                Used by Thingsboard to identify this device.
            rpc_map: ...
        """
        self._host = host
        self._port = port
        self._token = token

        self._client = mqtt.Client()
        self._client.username_pw_set(self._token)       
        self._client.on_connect = self._on_connect 
        self._client.on_publish = self._on_publish
        self._client.on_message = self._on_message

        self._rpc_map = rpc_map
        self._connected = False

    def _on_connect(self, client, userdata, flags, rc):
        """
        on_connect callback used by paho-mqtt, logs whether
        connection was successful.
        """
        if rc == 0:
            logger.info("MQTT: Connected successfully to Thingsboard.")
            self._client.subscribe("v1/devices/me/rpc/request/+")
            self._connected = True
        else:
            logger.warning(f"MQTT: Connection failed with error code '{rc}'")

    def _on_publish(self, client, userdata, mid):
        """
        on_publish callback for paho-mqtt, handles outgoing
        messages - no logic necessary.
        """
        ...

    def _on_message(self, client, userdata, msg):
        """
        on_message callback for paho-mqtt, handles incoming
        mqtt messages.
        """
        try:
            logger.info(f"MQTT: Recieved message on '{msg.topic}'")
            
            if msg.topic.startswith("v1/devices/me/rpc/request"):
                logger.info("MQTT: Processing inbound RPC request.")  # TODO: Handle logic.
                payload = json.loads(msg.payload.decode("utf-8"))
                method = payload.get("method")
                params = json.loads(payload.get("params", {}))

                if method in self._rpc_map:
                    logger.info(f"MQTT: Executing RPC method '{method}")
                    try:
                        response_payload = self._rpc_map[method](params)
                        logger.info(f"MQTT: Response: {response_payload}")
                    except Exception:
                        logger.exception(f"MQTT: Error executing RPC method.")
                        response_payload = {"status": "error", "message": "Unknown server error."}
                else:
                    logger.info("MQTT: Unknown RPC method '{method}'")
                    response_payload = {"status": "error", "message": "Unknown RPC method."}
                
                response_topic = f"v1/devices/me/rpc/response/{msg.topic.split('/')[-1]}"
                logger.info(response_topic)
                self._client.publish(response_topic, json.dumps(response_payload))
                
            else:  # NO RESPONSE, COULD NOT DECODE ETC.
                logger.error("MQTT: Could not process unknown MQTT message.")

        except Exception:
            logger.exception(f"MQTT: Exception processing message.")

    def connect(self):
        """Connect to the Thingsboard MQTT broker."""
        try:
            logger.info(f"MQTT: Attempting to connect to {self._host}:{self._port}...")
            self._client.connect(self._host, self._port, 60)
            self._client.loop_start()
            self._connected = True
        except Exception:
            logger.exception(f"MQTT: Error connecting...")
            self._connected = False

    def disconnect(self):
        """Disconnect from the Thingsboard MQTT broker."""
        ...

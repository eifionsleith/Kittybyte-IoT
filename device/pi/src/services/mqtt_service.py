from __future__ import annotations
import logging
import json
import paho.mqtt.client as mqtt
from typing import TYPE_CHECKING, Any, Callable, Dict

if TYPE_CHECKING:
    from .service_coordinator import ServiceCoordinator

logger = logging.getLogger(__name__)

class MqttService:
    """
    Handles MQTT communication between the device and 
    Thingsboard.
    """
    def __init__(self, host: str, port: int, token: str, rpc_map: Dict[str, Callable], coordinator: ServiceCoordinator):
        """
        Initializes the MqttService.

        Args:
            host (str): Thingsboard host, e.g. thingsboard.cs.cf.ac.uk
            port (int): Thingsboard MQTT port, e.g. 1883
            token (str): Thingsboard access token, generated during provisioning.
                Used by Thingsboard to identify this device.
            rpc_map (Dict[str, Callable]): A dictionary mapping RPC method names
                to callable functions to handle the requests.
            coordinator (ServiceCoordinator): ServiceCoordinator to interact with.
        """
        self._host = host
        self._port = port
        self._token = token
        self._rpc_map = rpc_map
        self._coordinator = coordinator
        
        self._client = mqtt.Client()
        self._client.username_pw_set(self._token)
        self._client.on_connect = self._on_connect
        self._client.on_publish = self._on_publish
        self._client.on_message = self._on_message

        self._connected = False

    def _on_connect(self, client, userdata, flags, rc):
        """
        on_connect callback used by paho-mqtt
        """
        if rc == 0:
            logger.info("Connected successfully to Thingsboard.")
            self._client.subscribe("v1/devices/me/rpc/request/+")
            self._connected = True
        else:
            logger.error(f"Thingsboard connection failed with code '{rc}")
            self._connected = False

    def _on_publish(self, client, userdata, mid):
        """
        on_publish callback used by paho-mqtt
        """
        logger.debug(f"MQTT message published with ID {mid}.")

    def _on_message(self, client, userdata, msg):
        """
        on_message callback used by paho-mqtt
        
        Handles incoming RPC requests.
        """
        try:
            logger.info(f"MQTT message received on topic '{msg.topic}")

            if msg.topic.startswith("v1/devices/me/rpc/request"):
                self._handle_rpc_request(msg)
            elif msg.topic.startswith("v1/devices/me/attributes/share"):
                ...
                # self._handle_shared_attributes_update(msg)
            else:
                logger.warning(f"Received MQTT message on unhandled topic: '{msg.topic}'")
        
        except Exception as e:
            logger.exception(f"MQTT Exception processing message: {e}")

    def _handle_rpc_request(self, msg):
        """
        Handles the incoming RPC request.
        """
        logger.info("Processing incoming RPC request.")
        rpc_request_id = msg.topic.split('/')[-1] # Last bit is the id 

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            method = payload.get("method")
            paramas_json = payload.get("params", "{}")
            params = json.loads(paramas_json)
                    
            response_payload = {  # Defaults
                    "status": "error",
                    "message": f"Unknown RPC method: {method}"
                    }
                    
            if method in self._rpc_map:
                logger.info("Executing MQTT method '{method}'.")
                try:
                    response_payload = self._rpc_map[method](params)
                except Exception as e:
                    error_msg = f"Error exectuing RPC method '{method}'"
                    logger.exception(error_msg)
                    response_payload = {
                            "status": "error",
                            "message": error_msg
                            }
            else:
                logger.warning(f"Unknown RPC method '{method}' received.")

        except json.JSONDecodeError:
            error_msg = "Failed to decode RPC request payload as JSON."
            logger.error(error_msg)
            response_payload = {
                    "status": "error",
                    "message": error_msg
                    }

        except Exception as e:
            logger.exception("An unexpected error occured during RPC processing.")
            response_payload = {
                    "status": "error",
                    "message": f"Unexpected error processing RPC: {e}"
                    }

        response_topic = f"v1/devices/me/rpc/response/{rpc_request_id}"
        logger.info(f"Publishing RPC response to topic: {response_topic}")
        self._client.publish(response_topic, json.dumps(response_payload))

    def _handle_shared_attributes_update(self, msg):
        """
        Handles incoming shared attributes update messages.
        """
        logger.info("Received shared attributes update.")
        try:
            attributes = json.loads(msg.payload.decode("utf-8"))
            self._coordinator.handle_attribute_update_from_mqtt(attributes)
        except json.JSONDecodeError:
            logger.error("Failed to decode shared attributed payload as JSON.")

    def connect(self):
        """
        Connect to the Thingsboard MQTT broker.
        """
        if self._connected:
            logger.info("MQTT already connected.")
            return

        try:
            self._client.connect(self._host, self._port, 60)
            self._client.loop_start()
        except Exception as e:
            logger.exception(f"Error attempint got connect to MQTT: {e}")

    def disconnect(self):
        """
        Disconnect from the Thingsboard MQTT broker.
        """
        if self._connected:
            try:
                self._client.loop_stop()
                self._client.disconnect()
                self._connected = False
                logger.info("MQTT disconnected successfully.")
            except Exception as e:
                logger.error(f"Error during MQTT disconnect: {e}")
        else:
            logger.info("MQTT not connected, no need to disconnect.")

    def is_connected(self) -> bool:
        """
        Checks if the MQTT client is currently connected.
        """
        return self._connected

    def publish_telemetry(self, telemetry_data: Dict[str, Any]):
        """
        Publishes telemetry data to Thingsboard.

        Args:
            telemetry_data (Dict[str, Any]): A dictionary containing
                telemetry key-value pairs.
        """
        if not self._connected:
            logger.warning("MQTT not connected, cannot publish telemetry.")
            return
        
        topic = "v1/devices/me/telemetry"
        try:
            payload = json.dumps(telemetry_data)
            self._client.publish(topic, payload)
        except Exception as e:
            logger.error(f"Error publishing MQTT telemetry: {e}")


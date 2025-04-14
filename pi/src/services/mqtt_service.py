from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import paho.mqtt.client as mqtt
import queue
import json

@dataclass
class RPCCommand:
    request_id: str
    method: str
    params: Dict[str, Any] = field(default_factory=dict)

class MQTTService:
    def __init__(self, host: str, port: int, token: str):
        """
        Args:
            host (str): Thingsboard host, e.g. thingsboard.cs.cf.ac.uk
            port (int): Thingboard MQTT Port, e.g. 1833
            token (str): Thingsboard access token, generated during provisioning
        """
        self._host = host
        self._port = port
        self._token = token
        self._client = mqtt.Client()
        self._client.username_pw_set(self._token)

        self._client.on_connect = self._on_connect
        self._client.on_publish = self._on_publish
        self._client.on_message = self._on_message

        self._rpc_queue = queue.Queue()
        self._connected = False

    # Paho MQTT Callbacks
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("MQTT: Connected successfully to Thingsboard.")
            self._client.subscribe("v1/devices/me/rpc/request/+")
            self._connected = True
        else:
            print(f"MQTT: Connection failed, code '{rc}'")
            self._connected = False

    def _on_publish(self, client, userdata, mid):
        ...

    def _on_message(self, client, userdata, msg):
        print(f"MQTT: Recieved message '{msg.payload.decode('utf-8')}'")
        try:
            request_id = msg.topic.split('/')[-1]
            payload = json.loads(msg.payload.decode('utf-8'))
            
            rpc_command = RPCCommand(
                    request_id=request_id,
                    method=payload.get('method'),
                    params=payload.get('params', {})
                    )

            self._rpc_queue.put(rpc_command)
            print(f"MQTT: Queued RPC command - {rpc_command}")
        
        except Exception as e:
            print(f"MQTT: Error processing message on {msg.topic} - {e}")

    def connect(self):
        """Connect to the MQTT broker"""
        try:
            print(f"MQTT: Attempting to connect to {self._host}:{self._port}...")
            self._client.connect(self._host, self._port, 60)
            self._client.loop_start()
        except Exception as e:
            print(f"MQTT: Error connecting - {e}")
            self._connected = False

    def disconnect(self):
        """Disconnect from the MQTT broker"""
        ...

    def is_connected(self) -> bool:
        """
        Check if the client is currently connected.

        Returns:
            bool: True if currently connected, False otherwise.
        """
        return self._connected

    def get_rpc_command(self) -> Optional[RPCCommand]:
        """
        Check for the next command in the queue.

        Returns:
            Optional[dict]: The next RPC command, or None if queue is empty.
        """
        try:
            return self._rpc_queue.get_nowait()
        except queue.Empty:
            return None

    def send_rpc_response(self, rpc_command: RPCCommand, response: dict) -> bool:
        """
        Sends a response for a given RPC Command - informing the backend API 
        whether the command was successfully executed.

        Args:
            rpc_command (RPCCommand): The command to respond to.
            response (dict): The response message to provide.

        Returns:
            bool: True if successfully acknowledged by Thingsboard
        """
        if not self._connected:
            print("MQTT Error: Cannot send RPC response, not connected.")
            return False

        response_topic = f"v1/devices/me/rpc/response/{rpc_command.request_id}"
        payload = json.dumps(response)
        result = self._client.publish(response_topic, payload)
        print(f"MQTT: Sending RPC response to {response_topic} - {payload}")
        return result.rc == mqtt.MQTT_ERR_SUCCESS

    def send_telemetry(self, values: dict):
        """
        Sends telemetary data to Thingsboard.

        Args:
            values (dict): Telemetary data to send.
        """
        if not self._connected:
            print("MQTT Error: Cannot send RPC response, not connected.")
            return False

        telemetary_topic = "v1/devices/me/telemetry"
        payload = json.dumps(values)
        result = self._client.publish(telemetary_topic, payload)
        print(f"MQTT: Sending telemetary data to {telemetary_topic} - {payload}")
        print(result)
        return result.rc == mqtt.MQTT_ERR_SUCCESS

    # Context handling
    def __enter__(self):
        self.connect()
        import time
        time.sleep(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


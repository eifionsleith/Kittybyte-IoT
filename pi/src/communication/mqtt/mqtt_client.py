import paho.mqtt.client as mqtt

class MQTTClient:
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

    # Context handling
    def __enter__(self):
        self.connect()
        import time
        time.sleep(1)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

from uuid import UUID
from pydantic import BaseModel
from tb_rest_client import RestClientCE
from tb_rest_client.rest import ApiException

class DeviceCredentials(BaseModel):
    credentialsType: str
    credentialsValue: str

class DeviceProvisioningException(Exception):
    """Raised if provisioning fails"""
    def __init__(self, response: dict):
        self.error_msg = response.get("errorMsg", "Unknown provisioning error.")
        self.status = response.get("status", "UNKNOWN")

class ThingsboardNotFoundException(Exception):
    """Raised if a item cannot be found"""
    def __init__(self, message: str = "Device not found in Thingsboard"):
        self.message = message

class ThingsboardBadResponseException(Exception):
    """Raised if a response could not be parsed"""
    def __init__(self, message: str = "Thingsboard response could not be parsed"):
        self.message = message

class ThingsboardUtils:
    @staticmethod
    def provision_device(client: RestClientCE,
                         device_name: str,
                         provision_key: str,
                         provision_secret: str
                         ) -> DeviceCredentials:
        """
        Provisions (and creates) a device within Thingsboard 

        Args:
            client (tb_rest_client.RestClientCE): Instance of Thingsboard REST Client 
            device_name (str): Unique device name to use in Thingsboard 
            provision_key (str): Thingsboard provisioning credentials, key 
            provision_secret (str): Thingsboard provisioning credentials, secret 

        Returns:
            DeviceCredentials: Valid MQTT communication credentials
        """
        body = {
                "deviceName": device_name,
                "provisionDeviceKey": provision_key,
                "provisionDeviceSecret": provision_secret
                }
        response: dict[str, str] = client.provision_device(body) # pyright: ignore[reportArgumentType, reportAssignmentType]
        if response.get("status") == "FAILURE":
            raise DeviceProvisioningException(response)

        return DeviceCredentials(**response)

    @staticmethod
    def get_device_id_by_name(client: RestClientCE, device_name: str) -> UUID:
        """
        Looks up the Thingsboard device ID for the given device name.

        Args:
            client (tb_rest_client.RestClientCE): Instance of Thingsboard REST Client
            device_name (str): Device name to look up

        Returns:
            UUID: UUID of the device with given name
        """
        try: device = client.get_tenant_device(device_name)
        except ApiException as e:
            if e.status == 404:
                raise ThingsboardNotFoundException()
            raise e

        if device.id is None:
            raise ThingsboardNotFoundException()
        
        try:
            device_id = UUID(device.id._id)
        except ValueError as e:
            raise ThingsboardBadResponseException("Could not parse UUID from Thingsboard response") from e
        return device_id


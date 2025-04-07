from typing import Optional
from uuid import UUID
from tb_rest_client.rest import ApiException
from tb_rest_client.rest_client_ce import Device, DeviceProfileId, RestClientCE

from utils.thingsboard.thingsboard_exceptions import DeviceProvisioningException, ThingsboardNotFoundException
from utils.thingsboard.thingsboard_models import DeviceCredentials

class ThingsboardUtils:
    @staticmethod
    def create_device(client: RestClientCE, device_name: str, profile_id: UUID, label: Optional[str] = None) -> Device:
        """
        
        """
        device_profile_id = DeviceProfileId(
                    id=str(profile_id),
                    entity_type="DEVICE_PROFILE"
                )
        device = Device(
                name=device_name,
                device_profile_id=device_profile_id,
                label=label
                )
        device = client.save_device(device)
        return device

    @staticmethod
    def provision_device(client: RestClientCE, device_name: str, provision_key: str, provision_secret: str) -> DeviceCredentials:
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
        try:
            device = client.get_tenant_device(device_name)
        except ApiException as e:
            if e.status == 404:
                raise ThingsboardNotFoundException("Device not found in Thingsboard") from e
            raise e  # Unknown error.
        
        if device.id is None: 
            raise ThingsboardNotFoundException("Device not found in Thingsboard")
    
        return UUID(device.id._id)


import json
import requests

class ProvisioningError(Exception):
    ...

class ProvisioningNetworkError(ProvisioningError):
    """
    Indicates a network or HTTP error during communication'
    with Thingsboard.
    """
    def __init__(self, message, status_code=None, response_text=None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class ProvisioningFailedError(ProvisioningError):
    """
    Indicates Thingsboard responded but reported provisioning 
    failure, typically due to conflicting identifiers.
    """
    def __init__(self, message, response_data):
        super().__init__(message)
        self.response_data = response_data

def thingsboard_provision_device(
        device_identifier: str, 
        thingsboard_host: str, 
        provision_key: str,
        provision_secret: str) -> str:
    """
    Attempts to provision a device in our thingsboard instance. 

    Args:
        device_identifier (str): Unique identifier for this device.
        thingsboard_host (str): Host for our thingsboard instance.
        provision_key (str): Provision key credentials, from thingsboard.
        provision_secret (str): Provision secret credentials, from thingsboard.

    Returns:
        str: Device access token to be used by the provisioned device.
    """
    _provision_endpoint = f"http://{thingsboard_host}/api/v1/provision"
    _provision_payload = {
            "provisionDeviceKey": provision_key,
            "provisionDeviceSecret": provision_secret,
            "deviceName": device_identifier
            }

    try:
        response = requests.post(_provision_endpoint, json=_provision_payload)
        response.raise_for_status()
        provision_response = response.json()

        if provision_response.get("status") == "SUCCESS" and "credentialsValue" in provision_response:
            device_access_token = provision_response["credentialsValue"]
            return device_access_token

        else:
            _message = f"Provisioning failed for device with identifier: {device_identifier}"
            raise ProvisioningFailedError(_message, response_data=provision_response)

    except requests.exceptions.HTTPError as e:
        _status_code = e.response.status_code
        _message = f"HTTP Error {_status_code} during provisioning for device with identifier: {device_identifier}."
        _response_text = None

        try:
            _response_text = e.response.text
        except Exception:
            ...

        raise ProvisioningNetworkError(_message, status_code=_status_code, response_text=_response_text) from e

    except requests.exceptions.RequestException as e:
        _message = f"Network error for device with identifier: {device_identifier}"
        raise ProvisioningNetworkError(_message) from e 

    except json.JSONDecodeError as e:
        _message = f"Failed to decode successful JSON response from thingsboard for device with identifier: {device_identifier}"
        raise ProvisioningError(_message) from e


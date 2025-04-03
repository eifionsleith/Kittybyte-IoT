import json
from typing import Optional
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

class ThingsboardAPIError(Exception):
    """
    Indicates a generic error communicating with the API.
    """
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class ThingsboardClient:
    def __init__(self, host: str, username: Optional[str] = None, password: Optional[str] = None):
        self.host = host
        self.base_url = f"https://{host}"
        self.username = username
        self.password = password
        self._jwt_token = None
        self._refresh_token = None
        self._session = requests.Session()

    def _get_headers(self, requires_auth: bool = True) -> dict:
        headers = {"Content-Type": "application/json"}
        if requires_auth:
            if not self._jwt_token:
                ... # login
            if self._jwt_token:
                headers["X-Authorization"] = f"Bearer: {self._jwt_token}"
            else:
                raise ThingsboardAPIError("Authentication is required for this route.")
        return headers

    def _login(self):
        """

        """
        if not self.username and self.password:
            raise ThingsboardAPIError("Username and password is required to log in.")

        login_endpoint = f"{self.base_url}:443/api/auth/login"
        credentials = {"username": self.username, "password": self.password}

        try:
            response = self._session.post(login_endpoint, json=credentials, timeout=10)
            response.raise_for_status()
            response_json = response.json()

            self._jwt_token = response_json.get("token")
            self._refresh_token = response_json.get("refreshToken")
            if not self._jwt_token and self._refresh_token:
                raise ThingsboardAPIError("Login successful, but JWT tokens could not be parsed.")

        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response is not None else None
            response_text = e.response.text if e.response is not None else None
            raise ThingsboardAPIError(f"Login Failed: {e}", status_code=status_code, response_text=response_text) from e
        
##! LEGACY
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


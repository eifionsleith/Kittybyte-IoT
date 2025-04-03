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

        login_endpoint = f"{self.base_url}/api/auth/login"
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

    def provision_device(self, device_identifier: str, provision_key: str, provision_secret: str) -> str:
        """
        Attempts to provision a device with given identifier (name) in the 
        thingsboard instance.

        Args:
            device_identifier (str): Unique name for this device, recommend UUID.
            provision_key (str): Credentials for the device type to provision.
            provision_secret (str): Credentials for the device type to provision.

        Returns:
            str: Device access token to be used by the provisioned device during 
                communications.
        """
        provision_endpoint = f"{self.base_url}/api/v1/provision"
        provision_payload = {
                "provisionDeviceKey": provision_key,
                "provisionDeviceSecret": provision_secret,
                "deviceName": device_identifier
                }

        try:
            response = self._session.post(provision_endpoint, json=provision_payload, timeout=10)
            response.raise_for_status()
            response_json = response.json()

        except requests.exceptions.RequestException as e:
            status_code = e.response.status_code if e.response is not None else None
            response_text = e.response.text if e.response is not None else None
            raise ThingsboardAPIError(f"Provisioning Failed: {e}", status_code=status_code, response_text=response_text) from e

        except json.JSONDecodeError as e:
            raise ThingsboardAPIError("Response recieved but could not decode JSON.")

        if not (response_json.get("status") == "SUCCESS" and "credentialsValue" in response_json):
            raise ThingsboardAPIError("Provisioning Failed")

        device_access_token = response_json["credentialsValue"]
        return device_access_token
        

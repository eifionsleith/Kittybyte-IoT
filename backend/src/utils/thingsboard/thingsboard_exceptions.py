class ThingsboardException(Exception):
    ...

class ThingsboardFailedRequestException(ThingsboardException):
    ...

class DeviceProvisioningException(ThingsboardFailedRequestException):
    """Raised when device provisioning failes."""
    def __init__(self, response: dict):
        self.error_msg = response.get("errorMsg", "Unknown provisioning error.")
        self.status = response.get("status", "UNKNOWN")

    def __str__(self) -> str:
        return f"Device provisioning failed: {self.error_msg} (status: {self.status})"

class ThingsboardNotFoundException(ThingsboardFailedRequestException):
    """Raised when query fails."""
    def __init__(self, message):
        self.message = message

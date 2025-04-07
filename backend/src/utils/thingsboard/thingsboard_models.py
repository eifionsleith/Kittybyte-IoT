from pydantic import BaseModel


class DeviceCredentials(BaseModel):
    credentialsType: str
    credentialsValue: str

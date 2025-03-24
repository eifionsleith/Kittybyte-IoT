from typing import Optional
from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: Optional[str] = None
    owner_id: Optional[int] = None

class DeviceCreate(DeviceBase):
    id: int

class DeviceUpdate(DeviceBase):
    ...

class DeviceDatabaseObject(DeviceBase):
    id: int


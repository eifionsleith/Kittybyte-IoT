from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class DeviceBase(BaseModel):
    user_defined_name: Optional[str] = None

class DeviceCreate(DeviceBase):
    ...

class DeviceOutput(DeviceBase):
    id: UUID

class DeviceUpdate(DeviceBase):
    user_defined_name: Optional[str] = None
    owner_id: Optional[UUID] = None


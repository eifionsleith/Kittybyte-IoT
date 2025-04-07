from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class DeviceBase(BaseModel):
    ...

class DeviceCreate(DeviceBase):
    ...

class DeviceUpdate(DeviceBase):
    owner_id: Optional[UUID]
    thingsboard_id: Optional[UUID]
    name: Optional[str]

class DeviceOutput(DeviceBase):
    id: UUID


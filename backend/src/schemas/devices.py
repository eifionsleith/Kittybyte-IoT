from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: Optional[str] = None

class DeviceCreate(DeviceBase):
    ...

class DeviceUpdate(BaseModel):
    owner_id: Optional[UUID] = None
    thingsboard_id: Optional[UUID] = None
    name: Optional[str] = None

class DeviceOut(DeviceBase):
    id: UUID

    class Config:
        from_attributes = True

class DeviceUserUpdate(BaseModel):
    name: Optional[str] = None


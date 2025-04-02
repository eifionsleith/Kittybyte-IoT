from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: Optional[str] = None

class DeviceCreate(DeviceBase):
    creator_id: UUID

class DeviceOutput(DeviceBase):
    id: UUID

class DeviceUpdate(DeviceBase):
    name: Optional[str] = None
    owner_id: Optional[UUID] = None


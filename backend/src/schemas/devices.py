from typing import Optional
from uuid import UUID
from pydantic import BaseModel

from src.schemas.schedule import ScheduleOut


class DeviceBase(BaseModel):
    name: Optional[str] = None

class DeviceCreate(DeviceBase):
    ...

class DeviceUpdate(BaseModel):
    owner_id: Optional[UUID] = None
    thingsboard_id: Optional[UUID] = None
    active_schedule_id: Optional[UUID] = None
    name: Optional[str] = None

class DeviceOut(DeviceBase):
    id: UUID
    active_schedule: ScheduleOut

    class Config:
        from_attributes = True

class DeviceUserUpdate(BaseModel):
    name: Optional[str] = None


from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.schemas.schedule_slot import ScheduleSlotCreate, ScheduleSlotOut


class ScheduleBase(BaseModel):
    description: str = Field(..., max_length=255)

class ScheduleCreate(ScheduleBase):
    name: str = Field(..., max_length=64)
    slots: List[ScheduleSlotCreate] = Field(..., min_length=1)

class ScheduleUpdate(ScheduleBase):
    name: Optional[str] = Field(None, max_length=64)

class ScheduleOut(ScheduleBase):
    id: UUID
    name: Optional[str] = Field(None, max_length=64)
    slots: List[ScheduleSlotOut] = [] # schedule slot out

    class Config:
        from_attributes = True


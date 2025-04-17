from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from src.schemas.schedule_slot import ScheduleSlotCreate, ScheduleSlotOut


class ScheduleBase(BaseModel):
    name: str = Field(..., max_length=64)

class ScheduleCreate(ScheduleBase):
    description: str = Field(..., max_length=255)
    slots: List[ScheduleSlotCreate] = Field(..., min_length=1)

class ScheduleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=64)
    slots: Optional[List[ScheduleSlotCreate]] = None

class ScheduleOut(ScheduleBase):
    id: UUID
    description: str = Field(..., max_length=255)
    slots: List[ScheduleSlotOut] = [] # schedule slot out

    class Config:
        from_attributes = True


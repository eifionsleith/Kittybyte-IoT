from datetime import time
from typing import Optional
from pydantic import BaseModel, Field, validator


class ScheduleSlotBase(BaseModel):
    day_of_week: int = Field(...)
    time_of_day: time
    amount: int

    @validator('amount')
    def validate_amount(cls, v):
        if not v > 0:
            raise ValueError("Amount must be positive.")
        return v

    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        if not 0 <= v <= 6:
            raise ValueError("Day of week must be between 0 and 6")
        return v

class ScheduleSlotCreate(ScheduleSlotBase):
    ...

class ScheduleSlotUpdate(BaseModel):
    ...

class ScheduleSlotOut(ScheduleSlotBase):
    class Config:
        from_attributes = True


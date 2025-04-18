from datetime import time
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field


class Slot(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, description="Day of the week (0 for Monday, 6 for Sunday).")
    time_of_day: time = Field(..., description="Time of the day.")
    amount: int = Field(..., ge=1, description="Amount to dispense at this time.")

class ScheduleConfig(BaseModel):
    id: UUID
    slots: List[Slot]


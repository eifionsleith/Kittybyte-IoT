from datetime import time
from typing import List
from uuid import UUID
from pydantic import BaseModel, Field

class Slot(BaseModel):
    """
    Represents a single schedules feeding time slot.
    """
    day_of_week: int = Field(..., ge=0, le=6, description="Day of the week (0 for Monday, \
                                                    6 for Sunday).")
    time_of_day: time = Field(..., description="Time of day for this feed.")
    amount: int = Field(..., ge=1, description="Amount of food to dispense at this time.")

class ScheduleConfig(BaseModel):
    """
    Represents the overall schedule configuration, containing
    multiple time slots.
    """
    id: UUID = Field(..., description="Unique identifier for this schedule configuration.")
    slots: List[Slot] = Field(default_factory=list, description="List of scheduled feeding\
                                                        time slots.")


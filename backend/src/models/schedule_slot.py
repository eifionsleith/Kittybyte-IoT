from datetime import time
import uuid
from sqlalchemy import UUID, ForeignKey, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import BaseDatabaseModel
from src.models.schedule import Schedule


class ScheduleSlot(BaseDatabaseModel):
    __tablename__ = "schedule_slots"
    schedule_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(Schedule.id), index=True, nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    time_of_day: Mapped[time] = mapped_column(Time, nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    schedule = relationship("Schedule", back_populates="slots")


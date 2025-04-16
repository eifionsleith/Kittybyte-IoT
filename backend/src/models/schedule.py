import uuid
from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import BaseDatabaseModel
from src.models.user import User


class Schedule(BaseDatabaseModel):
    __tablename__ = "schedules"
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(User.id), index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    
    owner = relationship("User", back_populates="schedules")
    slots = relationship("ScheduleSlot", back_populates="schedule", cascade="all, delete-orphan", passive_deletes=True)

from .schedule_slot import ScheduleSlot


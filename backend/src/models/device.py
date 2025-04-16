from datetime import datetime
import uuid
from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import BaseDatabaseModel
from src.models.user import User


class Device(BaseDatabaseModel):
    __tablename__ = "devices"
    thingsboard_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, unique=True, nullable=True)
    provisioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(User.id), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)
    
    owner = relationship("User", back_populates="owned_devices")


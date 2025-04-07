from datetime import datetime
from uuid import UUID as _UUID
from sqlalchemy import UUID, DateTime, ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship, Mapped
from models.base import BaseDatabaseModel
from models.user import User


class Device(BaseDatabaseModel):
    __tablename__ = "devices"

    #! IDs
    thingsboard_id: Mapped[_UUID] = mapped_column(UUID(as_uuid=True), index=True, unique=True, nullable=True)

    #! Timestamps
    provisioned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    #! Operational Data
    owner_id: Mapped[_UUID] = mapped_column(UUID(as_uuid=True), ForeignKey(User.id), index=True, nullable=True)
    name: Mapped[str] = mapped_column(String(64), nullable=True)

    #! Relationships
    owner = relationship("User", back_populates="owned_devices")


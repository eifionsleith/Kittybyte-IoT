import uuid
from sqlalchemy import UUID, Boolean, Column, DateTime, String, func # pyright: ignore
from sqlalchemy.orm import relationship
from utils.database import Base

class User(Base):
    __tablename__ = "users"

    ##! IDs
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)

    ##! Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_onupdate=func.now())

    ##! Operational Data 
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_superuser = Column(Boolean)

    ##! Relationships
    owned_devices = relationship(
            "Device",
            back_populates="owner",
            foreign_keys="[Device.owner_id]"
            )


import uuid
from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, func # pyright: ignore
from sqlalchemy.orm import relationship
from models.user import User
from utils.database import Base

class Device(Base):
    __tablename__ = "devices"
    
    ##! IDs
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    thingsboard_id = Column(UUID(as_uuid=True), index=True, unique=True)

    ##! Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_onupdate=func.now())
    provisioned_at = Column(DateTime(timezone=True)) # TODO: Trigger
    last_seen = Column(DateTime(timezone=True)) # TODO: Trigger

    ##! Operational Data 
    owner_id = Column(UUID(as_uuid=True), ForeignKey(User.id), index=True)
    user_defined_name = Column(String(255))

    ##! Relationships
    owner = relationship("User", back_populates="owned_devices", foreign_keys=owner_id)


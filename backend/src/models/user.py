import uuid
from sqlalchemy import UUID, Boolean, Column, String # pyright: ignore
from sqlalchemy.orm import relationship
from utils.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_superuser = Column(Boolean)

    owned_devices = relationship(
        "Device", 
        back_populates="owner", 
        foreign_keys="[Device.owner_id]" 
    )

    created_devices = relationship(
        "Device", 
        back_populates="creator", 
        foreign_keys="[Device.creator_id]" 
    )

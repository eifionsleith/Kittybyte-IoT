import uuid
from sqlalchemy import UUID, Column, ForeignKey, String # pyright: ignore
from sqlalchemy.orm import relationship
from models.user import User
from utils.database import Base


class Device(Base):
    __tablename__ = "devices"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey(User.id), index=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey(User.id), index=True)
    name = Column(String(255))
    owner = relationship("User", back_populates="owned_devices", foreign_keys=owner_id)
    creator = relationship("User", back_populates="created_devices", foreign_keys=creator_id)


import uuid
from sqlalchemy import UUID, Column, DateTime, func # pyright: ignore
from utils.database import Base

class BaseDatabaseModel(Base):
    """
    Fields common to all database models.
    """
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_onupdate=func.now())


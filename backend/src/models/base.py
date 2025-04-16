from datetime import datetime
import uuid
from sqlalchemy import UUID, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from src.utils.database import Base


class BaseDatabaseModel(Base):
    """Fields common to all database models"""
    __abstract__ = True
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_onupdate=func.now(), nullable=True)


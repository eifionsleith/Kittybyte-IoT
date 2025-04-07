from sqlalchemy import Boolean, String
from sqlalchemy.orm import mapped_column, relationship, Mapped
from models.base import BaseDatabaseModel


class User(BaseDatabaseModel):
    __tablename__ = "users"
    
    #! Operational Data
    email: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    #! Relationships
    owned_devices = relationship("Device", back_populates="owner")

from models.device import Device  # This is necessary.


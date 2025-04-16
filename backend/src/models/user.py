from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import BaseDatabaseModel


class User(BaseDatabaseModel):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    owned_devices = relationship("Device", back_populates="owner")
    schedules = relationship("Schedule", back_populates="owner")

from .device import Device  # Necessary


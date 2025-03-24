from sqlalchemy import Column, ForeignKey, Integer, String
from utils.database import Base
from models.user import User


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey(User.id), index=True)
    name = Column(String(255))

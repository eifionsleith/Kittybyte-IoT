from sqlalchemy import Column, ForeignKey, Integer
from utils.database import Base
from models.user import User


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: Optional[EmailStr] = None

class UserRegister(UserBase):
    password: str

class UserOutput(UserBase):
    id: UUID

class UserUpdate(UserBase):
    password: Optional[str] = None
    is_superuser: Optional[bool] = None


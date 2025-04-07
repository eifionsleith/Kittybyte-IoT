from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None
    is_superuser: bool = False

class UserOutput(UserBase):
    id: UUID

class UserOutputAdmin(UserOutput):
    email: EmailStr
    is_superuser: bool


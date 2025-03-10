from pydantic import EmailStr, BaseModel

class UserBase(BaseModel):
    email: EmailStr

class UserRegister(UserBase):
    password: str

class UserInDb(UserBase):
    password_hash: str

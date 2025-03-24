from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """
    Base fields for the User.
    """
    email: EmailStr

class UserRegister(UserBase):
    """
    Used for user registration, contains plaintext password.
    """
    password: str

class UserDatabaseObject(UserBase):
    """
    Used for storage inside the database, contains password hash.
    """
    password_hash: str

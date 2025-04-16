from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str

class Success(BaseModel):
    message: str
    success: bool = True


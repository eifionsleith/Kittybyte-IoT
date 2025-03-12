from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session

from config import config
from crud.user import user_crud_interface
from database import get_db
from models.user import User
from schemas.auth import TokenData

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

##! TODO -> Tidy types, CRUDInterface still returns BaseModel
def get_current_user(
        token: Annotated[str, Depends(oauth2_schema)],
        db: Annotated[Session, Depends(get_db)]) -> User:
    """
    Decodes the given JWT Token and returns the relevant User
    from the database.
    """
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate user.",
            headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
        
    except jwt.exceptions.InvalidTokenError:
        raise credentials_exception
    
    user = user_crud_interface.get_one(db, User.id == token_data.user_id)
    if user is None:
        raise credentials_exception

    return user


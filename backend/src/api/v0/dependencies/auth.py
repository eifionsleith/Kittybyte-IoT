import jwt
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.v0.dependencies.database import get_db
from models.user import User
from schema.auth import TokenData
from utils.settings import get_settings
from crud.user import crud_user

oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_user_from_jwt(
        token: Annotated[str, Depends(oauth2_schema)],
        db: Annotated[Session, Depends(get_db)]) -> User:
    """
    Decodes a JWT and returns the relevant User from the database if valid.
    """
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate user from provided JWT",
            headers={"WWW-Authenticate": "Bearer"})
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)

    except jwt.exceptions.InvalidTokenError:
        raise credentials_exception

    user = crud_user.get_one(db, User.id == token_data.user_id)
    if user is None:
        raise credentials_exception

    return user


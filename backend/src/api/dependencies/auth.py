from uuid import UUID
import jwt
from typing import Annotated
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.dependencies.database import get_db
from models.user import User
from schema.auth import TokenData
from utils.config import AppConfig
from crud.user import user_crud_interface


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_user_from_jwt(
        token: Annotated[str, Depends(oauth2_schema)],
        db: Annotated[Session, Depends(get_db)],
        request: Request) -> User:
    """
    Decodes a JWT and returns the relvant User from the database
    if subject is a valid User's UUID.
    """
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate user from provided JWT",
            headers={"WWW-Authenticate": "Bearer"})
    config: AppConfig = request.app.state.config

    try:
        payload = jwt.decode(token, config.jwt_secret, algorithms=[config.jwt_algorithm])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except jwt.exceptions.InvalidTokenError:
        raise credentials_exception
    
    try:
        user_uuid = UUID(token_data.user_id)
    except ValueError:
        raise credentials_exception

    user = user_crud_interface.get_one(db, User.id == user_uuid)
    if user is None:
        raise credentials_exception
    return user

def get_current_superuser(current_user: Annotated[User, Depends(get_user_from_jwt)]) -> User:
    """
    Returns the current superuser.

    Args:
        current_user (User, optional): The current user.

    Returns:
        user: The current superuser.

    Raises:
        HTTPException: (403) If the current user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have sufficient privileges.")
    
    return current_user


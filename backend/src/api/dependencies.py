from typing import Annotated, Generator

import jwt
from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from tb_rest_client import RestClientCE

from crud.user import user_crud_interface
from models.user import User
from utils.config import AppConfig
from utils.database import Database


oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db(request: Request) -> Generator[Session, None, None]:
    """
    Creates a database session from the AppConfig

    Args:
        request (Request): Request containing the app state.
    """
    config: AppConfig = request.app.state.config
    db = Database(config.db.uri, echo=config.db.echo_all).get_db()
    yield from db

def get_thingsboard_client(request: Request) -> RestClientCE:
    return request.app.state.thingsboard_handler.get_client()

def get_config(request: Request) -> AppConfig:
    return request.app.state.config

def get_current_user(
        token: Annotated[str, Depends(oauth2_schema)],
        db: Annotated[Session, Depends(get_db)],
        request: Request) -> User:
    """
    Takes a JWT string and retreives the user subject from the database, assuming
    the JWT is a valid token issued by us.

    Args:
        token (str): The JWT token to get user from. Retrieved by the oauth2_schema dependency.
        db (Session): Database session to interact with. Retrieved by the get_db dependency.
        request (Request): Request containing the app state.
    
    Returns:
        User: The user described by the JWT token.

    Raises:
        HTTPException: 401 if the provided token cannot be decoded or validated.
    """
    credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate user from provided JWT",
            headers={"WWW-Authenticate": "Bearer"}
            )
    config: AppConfig = request.app.state.config

    try:
        payload = jwt.decode(token, config.jwt.secret, algorithms=[config.jwt.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = UUID(user_id)

    except (jwt.exceptions.InvalidTokenError, ValueError):
        raise credentials_exception

    user = user_crud_interface.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user

def get_current_superuser_from_jwt(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Takes a User and returns them if they have superuser permission.

    Args:
        current_user (User): The user to check for. Retrieved by get_current_user dependency.

    Returns:
        User: The current user, if they are a superuser.

    Raises:
        HTTPException: 403 if the current user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have sufficient permissions."
                )

    return current_user


from uuid import UUID
import jwt
from typing import Annotated, Generator
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from tb_rest_client import RestClientCE

from src.crud.user import user_crud_interface
from src.models.user import User
from src.utils.config import AppSettings
from src.utils.database import Database

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_settings(request: Request) -> AppSettings:
    """
    Gets the AppSettings object from the app state.

    Args:
        request (fastapi.Request): Contains the app state, handled by FastAPI.
    """
    return request.app.state.settings

def get_db(settings: Annotated[AppSettings, Depends(get_settings)]) -> Generator[Session, None, None]:
    """Gets a database session."""
    db = Database(settings.db.uri, settings.db.echo_all).get_db()
    yield from db

def get_tb_client(request: Request) -> RestClientCE:
    """Gets the Thingsboard client"""
    return request.app.state.thingsboard_handler.get_client()

def get_current_user(token: Annotated[str, Depends(oauth2_schema)],
                     db: Annotated[Session, Depends(get_db)],
                     settings: Annotated[AppSettings, Depends(get_settings)]
                     ) -> User:

    """
    Takes a JWT and returns the user subject from the database,
    assuming the token is valid.
    """
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not authenticate user.",
                                          headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, settings.jwt.secret, algorithms=[settings.jwt.algorithm])
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

def get_current_superuser(user: Annotated[User, Depends(get_current_user)]
                          ) -> User:
    """
    Gets the current user, and returns them if they are a superuser.
    """
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="User does not have sufficient privileges.")
    return user


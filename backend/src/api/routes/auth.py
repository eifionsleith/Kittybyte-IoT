from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.dependencies import get_current_superuser_from_jwt, get_db
from crud.user import user_crud_interface
from schema.auth import Token
from schema.user import UserCreate, UserOutput, UserOutputAdmin
from utils.config import AppConfig
from utils.security import create_jwt


router = APIRouter()
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOutput)
def register_user(user_creation_schema: UserCreate,
                  db: Annotated[Session, Depends(get_db)]) -> UserOutput:
    """ 
    Takes data in request body of form UserCreate, and attempts
    to create a new user in the database with these credentials,
    assuming user with same email or username does not already exist.
    """
    try:
        user_crud_interface.validate_creation_schema(db, user_creation_schema)
    except ValueError as e:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
                )

    user = user_crud_interface.create(db, user_creation_schema)
    return user

@router.post("/login", response_model=Token)
def login_user_for_access_token(db: Annotated[Session, Depends(get_db)],
                                form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                request: Request) -> Token:
    """
    Takes data in request body of form OAuth2PasswordRequestForm
    and attempts to validate this against registered users, returning
    a JWT token if credentials are valid.
    """
    config: AppConfig = request.app.state.config
    user = user_crud_interface.validate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
                headers={"WWW-Authenticate": "Bearer"}
                )

    token_expiry = timedelta(minutes=config.jwt.expiry_minutes)
    token = create_jwt(user.id, token_expiry, config.jwt.secret, config.jwt.algorithm)
    return Token(access_token=token, token_type="bearer")

#! TODO: /user/ route instead
@router.patch("/{target_username}/superuser", response_model=UserOutputAdmin, dependencies=[Depends(get_current_superuser_from_jwt)])
def set_user_is_superuser(db: Annotated[Session, Depends(get_db)],
                          target_username: str,
                          is_superuser: bool) -> UserOutputAdmin:
    """
    Sets superuser permissions for a provided user. Current user must have
    superuser permissions.
    """
    user = user_crud_interface.get_by_username(db, target_username)
    if user is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
                )

    user = user_crud_interface.set_is_superuser(db, user, is_superuser)
    return user


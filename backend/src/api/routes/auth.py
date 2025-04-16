from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.dependencies import get_db, get_settings
from src.schemas.misc import Token
from src.schemas.user import UserCreate, UserOut
from src.crud.user import UserConflictError, user_crud_interface
from src.utils.config import AppSettings
from src.utils.security import create_jwt


router = APIRouter()
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
def register_user(user_creation_schema: UserCreate,
                  db: Annotated[Session, Depends(get_db)]
                  ) -> UserOut:
    """
    Creates a new user with the given data, assuming username and 
    email do not currently exist in the database.
    """
    try:
        user_crud_interface.validate_creation_schema(db, user_creation_schema)
    except UserConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=str(e))

    user = user_crud_interface.create(db, user_creation_schema)
    return user

@router.post("/login", response_model=Token)
def login_user_for_access_token(db: Annotated[Session, Depends(get_db)],
                                settings: Annotated[AppSettings, Depends(get_settings)],
                                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
                                ) -> Token:
    """
    Takes a username and password, checks against the database 
    and returns a JWT access token if credentials are valid.
    """
    user = user_crud_interface.get_by_username(db, form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials.",
                            headers={"WWW-Authenticate": "Bearer"})

    token_exp = timedelta(minutes=settings.jwt.expiry_minutes)
    token = create_jwt(user.id, token_exp, settings.jwt.secret, settings.jwt.algorithm)
    return Token(access_token=token, token_type="bearer")


from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from schemas.auth import Token
from crud.user import user_crud_interface
from config import config
from schemas.user import UserInDb, UserRegister
from security import create_jwt
import security


auth_router = APIRouter()

@auth_router.post("/login", response_model=Token)
def login_for_access_token(
        db: Annotated[Session, Depends(get_db)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    Takes valid Username/Password form data and issues
    a JWT Access Token for the given user.
    """
    user = user_crud_interface.get_user_by_email(db, form_data.username)

    if not user:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
                headers={"WWW-Authenticate": "Bearer"})

    access_token_expiry = timedelta(minutes=config.jwt_access_token_expiry_minutes)
    access_token = create_jwt(user.id, access_token_expiry)
    return Token(access_token=access_token, token_type="bearer")

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user_register: UserRegister, db: Annotated[Session, Depends(get_db)]):
    """
    Checks if user already exists, and creates a new user if not.
    """
    user = user_crud_interface.get_user_by_email(db, user_register.email)
    if user:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists with provided email.")

    user_in_db = UserInDb(**user_register.model_dump(exclude_none=True, exclude_unset=True),
                          password_hash=security.get_password_hash(user_register.password))

    user = user_crud_interface.create(db, user_in_db)
    return {"message": "User created successfully."}


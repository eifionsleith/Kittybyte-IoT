from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.dependencies.auth import get_user_from_jwt
from api.dependencies.database import get_db
from crud.user import user_crud_interface
from models.user import User
from schema.auth import Token
from schema.user import UserOutput, UserRegister
from utils.config import AppConfig
from utils.security import create_jwt

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOutput)
def register_user(
        user_register: UserRegister,
        db: Annotated[Session, Depends(get_db)]) -> UserOutput:
    """
    Takes data in form UserRegister and attempts to create a new user 
    with such details.
    """
    user = user_crud_interface.get_by_email(db, user_register.email)
    if user:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email '{user_register.email}' already exists.")
    
    user = user_crud_interface.create(db, user_register)
    return user

@router.post("/login", response_model=Token)
def login_for_access_token(
        db: Annotated[Session, Depends(get_db)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        request: Request) -> Token:
    """
    Takes data in the form OAuth2PasswordRequestForm and returns a
    JWT access token if the provided credentials are valid.
    """
    config: AppConfig = request.app.state.config
    user = user_crud_interface.validate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
                headers={"WWW-Authenticate": "Bearer"})
    
    token_expiry = timedelta(minutes=config.jwt_expiry_minutes)
    token = create_jwt(user.id, token_expiry, config.jwt_secret, config.jwt_algorithm)
    return Token(access_token=token, token_type="bearer")

#! Example protected route, can be removed later
@router.get("/auth_test")
def auth_test(user: Annotated[User, Depends(get_user_from_jwt)]):
    return {"message": f"You are logged in as {user.id}"}


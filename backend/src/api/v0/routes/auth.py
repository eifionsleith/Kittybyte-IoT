from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.v0.dependencies.auth import get_user_from_jwt
from api.v0.dependencies.database import get_db
from models.user import User
from schema.auth import Token
from schema.user import UserDatabaseObject, UserRegister
from utils.security import Security
from crud.user import crud_user
from utils.settings import get_settings

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
        user_register: UserRegister,
        db: Annotated[Session, Depends(get_db)]):
    """
    Takes UserRegister data and attempts to create such user in the database if doesn't yet exist.
    """
    user = crud_user.get_by_email(db, user_register.email)
    if user:
        raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists.")
    
    user_in_db = UserDatabaseObject(**user_register.model_dump(exclude_none=True, exclude_unset=True),
                                    password_hash=Security.get_password_hash(user_register.password))
    user = crud_user.create(db, user_in_db)
    return {"message": "User created succesfully."}

@router.post("/login", response_model=Token)
def login_for_access_token(
        db: Annotated[Session, Depends(get_db)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    Takes a username and password form data, and issues a JWT access token if valid.
    """
    settings = get_settings()
    user = crud_user.validate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
                headers={"WWW-Authenticate": "Bearer"})

    token_expiry = timedelta(minutes=settings.jwt_access_token_expiry_minutes)
    token =  Security.create_jwt(user.id, token_expiry)
    return Token(access_token=token, token_type="bearer")

##! Example auth usage:
@router.get("/")
def example_protected_route(current_user: Annotated[User, Depends(get_user_from_jwt)]):
    return {"message": f"Currently logged in as '{current_user.email}'"}

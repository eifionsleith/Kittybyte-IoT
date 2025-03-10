from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from config import config
from database import get_db
from crud.user import user_crud_interface
from schemas.user import UserInDb, UserRegister
import security

auth_router = APIRouter()

##! TODO -> Tidy types.
@auth_router.post("/login")
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_crud_interface.get_user_by_email(db, form_data.username)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password.")

    access_token_expires = timedelta(minutes=config.jwt_access_token_expiry_minutes)
    access_token = security.create_jwt(user.id, access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_register: UserRegister, db: Session = Depends(get_db)) -> dict:
    user = user_crud_interface.get_user_by_email(db, user_register.email)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User exists with {user_register.email}")

    user_in_db = UserInDb(**user_register.model_dump(exclude_none=True, exclude_unset=True), 
                          password_hash=security.get_password_hash(user_register.password))

    user = user_crud_interface.create(db, user_in_db)
    return {"message": f"User {user.email} successfully created."}


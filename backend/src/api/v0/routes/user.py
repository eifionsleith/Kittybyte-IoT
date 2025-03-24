from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.v0.dependencies.auth import get_user_from_jwt
from api.v0.dependencies.database import get_db
from models.user import User
from crud.device import device_crud_interface

router = APIRouter()

@router.get("/me/devices")
def get_current_user_devices(
        db: Annotated[Session, Depends(get_db)],
        current_user: Annotated[User, Depends(get_user_from_jwt)]):
    return device_crud_interface.get_many_with_owner(db, current_user.id)


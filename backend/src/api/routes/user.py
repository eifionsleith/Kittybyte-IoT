from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, get_db
from src.crud.user import UserConflictError, user_crud_interface
from src.models.user import User
from src.schemas.user import UserOut, UserUpdate


router = APIRouter()

@router.get("/me", response_model=UserOut)
def get_user_me(user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    """
    Gets the current authenticated user's details.
    """
    return user

@router.put("/me", response_model=UserOut)
def update_user_me(user: Annotated[User, Depends(get_current_user)],
                   db: Annotated[Session, Depends(get_db)],
                   user_update: UserUpdate
                   ) -> UserOut:
    """
    Updates the current authenticated user's details.
    """
    try:
        updated_user = user_crud_interface.update(db, user, user_update)
    except UserConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=e.message)
    return updated_user


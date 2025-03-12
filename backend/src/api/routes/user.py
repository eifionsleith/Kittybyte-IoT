from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies.auth_dependencies import get_current_user
from models.user import User


user_router = APIRouter()

@user_router.get("/me")
def get_user_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Example protected route, returns current user object (excluding password_hash).
    """
    current_user_dict = current_user.__dict__
    current_user_excluding_password_hash = {x: current_user_dict[x] for x in current_user_dict if x not in "password_hash"}
    return current_user_excluding_password_hash

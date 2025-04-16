from typing import Optional
from sqlalchemy.orm import Session
from src.crud.base import CRUDBase
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate
from src.utils.security import get_password_hash, verify_password


class UserConflictError(Exception):
    def __init__(self, message):
        self.message = message

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return self.get_one(db, self.model.email == email)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return self.get_one(db, self.model.username == username)

    def create(self, db: Session, obj_in: UserCreate) -> User:
        db_obj = User(email=obj_in.email,
                      username=obj_in.username,
                      password_hash=get_password_hash(obj_in.password))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_update: UserUpdate) -> User:
        update_data = obj_update.model_dump(exclude_unset=True)

        if "email" in update_data:
            if self.get_by_email(db, update_data["email"]):
                raise UserConflictError("Email already exists.")

        if "username" in update_data:
            if self.get_by_username(db, update_data["username"]):
                raise UserConflictError("Username already exists.")

        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data["password"])
            del update_data["password"]

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Validates a username and password against the registered details,
        returning the matching user if valid.

        Args:
            db (session): Database session to interact with.
            username (str): Username to authenticate.
            password (str): Password to check.

        Returns:
            Optional[User]: The matching User object, if credentials are valid.
        """
        user = self.get_by_username(db, username)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def is_superuser(self, user: User) -> bool:
        """
        Checks if the provided user is a superuser.

        Args:
            user (User): User to check.

        Returns:
            bool: True if is a superuser.
        """
        return user.is_superuser

    def set_is_superuser(self, db: Session, user: User, is_superuser: bool) -> User:
        """
        Sets the is_superuser property of the provided user.

        Args:
            user (User): User to modify.
            is_superuser (bool): Whether to be superuser or not.

        Returns:
            User: Updated user.
        """
        user.is_superuser = is_superuser
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def validate_creation_schema(self, db: Session, creation_schema: UserCreate) -> None:
        """
        Validates a UserCreate schema, raising an exception if invalid.

        Args:
            db (Session): Database session to interact with.
            creation_schema (UserCreate): User to check if valid to create.

        Raises:
            UserConflictError: If user with either email or username already exists.
        """
        if self.get_by_email(db, creation_schema.email):
            raise UserConflictError("Email already exists.")
        if self.get_by_username(db, creation_schema.username):
            raise UserConflictError("Username already exists.")

user_crud_interface = CRUDUser(User)


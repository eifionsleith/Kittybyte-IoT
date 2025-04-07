from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from crud.base import CRUDBase
from models.user import User
from schema.user import UserCreate, UserUpdate
from utils.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def create(self, db: Session, obj_in: UserCreate) -> User:
        hashed_password = get_password_hash(obj_in.password)
        user = User(**obj_in.model_dump(exclude_none=True, exclude_unset=True, exclude={"password"}),
                    password_hash=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Args:
            db (Session): Database session to interact with.
            email (str): Email address to lookup.

        Returns:
            Optional[User]: The matching user, if found.
        """
        return self.get_one(db, self._model.email == email)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        Args:
            db (Session): Database session to interact with.
            username (str): Username to lookup.

        Returns:
            Optional[User]: The matching user, if found.
        """
        return self.get_one(db, self._model.username == username)
    
    def get_by_id(self, db: Session, id: UUID) -> Optional[User]:
        """
        Args:
            db (Session): Database session to interact with.
            id (UUID): User ID to lookup.
        """
        return self.get_one(db, self._model.id == id)

    def validate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Validates a username and password against the registered details, returning
        the matching user if these credentials are valid.

        Args:
            db (Session): Dataabse session to interact with.
            username (str): Username to lookup.
            password (str): Password to validate.

        Returns:
            Optional[User]: The matching user, if credentials are valid.
        """
        user = self.get_one(db, self._model.username == username)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def set_is_superuser(self, db: Session, user: User, is_superuser: bool) -> User:
        """
        Sets the is_superuser permission of the provided user.

        Args:
            db (Session): Dataabse session to interact with.
            user (User): User to change permissions for.
            is_superuser (bool): Whether this user should be a superuser or not.

        Returns:
            User: The updated user.
        """
        user.is_superuser = is_superuser
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def validate_creation_schema(self, db: Session, creation_schema: UserCreate):
        if self.get_by_email(db, creation_schema.email):
            raise ValueError("Email already exists.")
        if self.get_by_username(db, creation_schema.username):
            raise ValueError("Username already exists.")

user_crud_interface = CRUDUser(User)


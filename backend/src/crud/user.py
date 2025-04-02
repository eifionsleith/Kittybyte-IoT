from typing import Optional
from sqlalchemy.orm import Session
from crud.base import CRUDBase
from models.user import User
from schema.user import UserRegister, UserUpdate
from utils.security import get_password_hash, verify_password

 
class UserCRUD(CRUDBase[User, UserRegister, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Gets the first user matching the given email.
        """
        return self.get_one(db, self._model.email == email)

    def create(self, db: Session, obj_in: UserRegister) -> User:
        """
        Creates a new user in the database, handling hashing.
        """
        hashed_password = get_password_hash(obj_in.password)
        user = User(**obj_in.model_dump(exclude_none=True, exclude_unset=True, exclude={"password"}), password_hash=hashed_password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def validate_user(self, db: Session, username: str, password: str):
        """
        Takes a username and password, and returns the respective user 
        from the database, assuming the credentials are valid.

        Args:
            db (Session): A local database session. 
            username (str): Desired user's username. 
            password (str): Desired user's password.

        Returns:
            Optional[User]: The user, if the credentials match.
        """
        user = self.get_by_email(db, username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None

        return user

user_crud_interface = UserCRUD(User)

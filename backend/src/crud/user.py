from typing import Optional
from sqlalchemy.orm import Session
from crud.base import CRUDBase
from schema.user import UserDatabaseObject
from models.user import User
from utils.security import Security


class CRUDUser(CRUDBase[User, UserDatabaseObject, UserDatabaseObject]):
    def validate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Takes a username and password, and returns the given user from 
        the database, assuming the username and password match.
        """
        user = self.get_one(db, self.model.email == email)
        if not user:
            return None
        if not Security.verify_password(password, str(user.password_hash)):
            return None

        return user
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Gets the first user matching the given email.
        """
        return self.get_one(db, self.model.email == email)

crud_user = CRUDUser(User)


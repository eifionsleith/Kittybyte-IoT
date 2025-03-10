from typing import Optional

from sqlalchemy.orm import Session

from security import verify_password
from crud.base import CRUDInterface
from models.user import User


##! TODO -> Tidy up types.
class UserCRUDInterface(CRUDInterface):
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        return self.get_one(db, self._model.email == email)

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None

        return user

user_crud_interface = UserCRUDInterface(model=User)


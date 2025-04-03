from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session
from schema.user import UserRegister, UserUpdate
from utils.config import get_config
from utils.database import Database
from crud.user import user_crud_interface

SUPERUSER_EMAIL = "admin@example.com"
SUPERUSER_PASSWORD = "s3cur3"

config = get_config()
database = Database(config.db_uri, True)
database.initialize_database()

@contextmanager 
def get_database_session(database: Database) -> Generator[Session, None, None]:
    db_generator = database.get_generator()
    session = next(db_generator)
    try:
        yield session
    finally:
        session.close()

with get_database_session(database) as db:
    existing_user = user_crud_interface.get_by_email(db, SUPERUSER_EMAIL)

    if existing_user:
        print (f"User with email '{SUPERUSER_EMAIL}' already exists.")
    else:
        print(f"Creating superuser with email: {SUPERUSER_EMAIL}")
        user = user_crud_interface.create(db, UserRegister(email=SUPERUSER_EMAIL, password=SUPERUSER_PASSWORD))
        user_crud_interface.update(db, user, UserUpdate(is_superuser=True))


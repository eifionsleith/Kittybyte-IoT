from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from crud.user import user_crud_interface
from schema.user import UserCreate
from utils.config import get_config
from utils.database import Database


SUPERUSER_USERNAME = "admin"
SUPERUSER_PASSWORD = "secure"
SUPERUSER_EMAIL = "admin@thingsboard.org"

config = get_config(env_file=".env.dev")
database = Database(config.db.uri, True)
database.initalize_tables()

@contextmanager 
def get_database_session(database: Database) -> Generator[Session, None, None]:
    db_generator = database.get_db()
    session = next(db_generator)
    try: yield session
    finally: session.close()

with get_database_session(database) as db:
    admin_user_create = UserCreate(
            username=SUPERUSER_USERNAME,
            password=SUPERUSER_PASSWORD,
            email=SUPERUSER_EMAIL
            )
    try: user_crud_interface.validate_creation_schema(db, admin_user_create)
    except ValueError:
        print(f"User with email {SUPERUSER_EMAIL} or username {SUPERUSER_USERNAME} already exists!")
        raise

    user = user_crud_interface.create(db, admin_user_create)
    user_crud_interface.set_is_superuser(db, user, True)
    print("Superuser created!")

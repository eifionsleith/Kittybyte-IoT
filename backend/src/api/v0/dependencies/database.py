from typing import Generator
from sqlalchemy.orm import Session
from utils.database import Database
from utils.settings import get_settings

def get_db() -> Generator[Session, None, None]:
    """
    Gets a database session for the using the environment variables.
    """
    settings = get_settings()
    db = Database(settings.database_url, echo=settings.database_echo_all).get_generator()
    yield from db

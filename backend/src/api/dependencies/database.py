from typing import Generator

from fastapi import Request
from sqlalchemy.orm import Session

from utils.config import AppConfig
from utils.database import Database


def get_db(request: Request) -> Generator[Session, None, None]:
    """
    Creates a database session using the environment variables.
    """
    config: AppConfig = request.app.state.config
    db = Database(config.db_uri, echo=config.db_echo_all).get_generator()
    yield from db


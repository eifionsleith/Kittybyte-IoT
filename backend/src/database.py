from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import config

"""
Base class for SQLAlchemy Models.
"""
Base = declarative_base() # Maybe move?

def get_engine(database_url: str, echo: bool = False) -> Engine:
    """
    Creates and returns a SQLAlchemy Engine object to connect to our database.
    """
    # check_same_thread = False -> This is required for sqlite
    engine = create_engine(database_url, echo=echo, connect_args={"check_same_thread": False})
    return engine

def get_db() -> Generator:
    """
    Returns a Generator object that yields a local database session.
    """
    engine = get_engine(config.database_url, config.database_echo_all)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize the database, creating all tables.
    """
    engine = get_engine(config.database_url, config.database_echo_all)
    Base.metadata.create_all(bind=engine)


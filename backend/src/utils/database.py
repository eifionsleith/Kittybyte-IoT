from typing import Generator
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker 

## Base class for all SQLAlchemy models
Base = declarative_base()

class Database:
    def __init__(self, database_uri: str, echo: bool = False):
        """
        Initialize the Database object with the given settings.

        Args:
            database_uri (str): URI for the database to connect to.
            echo (bool): Whether to echo all SQL statements to the console,
                for debugging purposes. Defaults to False.
        """
        self._uri = database_uri
        self._echo = echo
        self._engine = self.get_engine()

    def get_engine(self) -> Engine:
        """
        Creates and returns a SQLAlchemy Engine Object for our database connection.

        Returns:
            Engine: SQLAlchemy Engine Object for the database connection.
        """
        connect_args = { "check_same_thread": False } # Required for SQLite
        engine = create_engine(self._uri, echo=self._echo, connect_args=connect_args)
        return engine
    
    def get_generator(self) -> Generator:
        """
        Creates and returns a Generator object that yields a local database connection.

        Returns:
            Generator: Yields a local database connection.
        """
        sessionmaker_kwargs = { "autocommit": False, "autoflush": False, "bind": self._engine }
        session = sessionmaker(**sessionmaker_kwargs)
        db = session()

        try: yield db
        finally: db.close()                                

    def initialize_database(self):
        """
        Initialize database, creating all tables. Required for first run.
        """
        Base.metadata.create_all(bind=self._engine)


from typing import Generator
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker 

## Base class for all SQLAlchmey Models.
Base = declarative_base()

class Database:
    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize the Database object with the given URL and echo settings.

        Args:
            database_url (str): URL for the database connection.
            echo (bool): Whether to echo all SQL statements to the console for debugging. 
                Defaults to False.
        """
        self.database_url = database_url
        self.echo = echo
        self.engine = self.get_engine()
    
    def get_engine(self) -> Engine:
        """
        Creates and returns a SQLAlchemy Engine Object for our database connection.

        Returns:
            Engine: SQLAlchmey Engine Object for this database connection.
        """
        # "check_same_thread = False" is required for sqlite
        connect_args = {"check_same_thread": False}
        engine = create_engine(self.database_url, echo=self.echo, connect_args=connect_args)
        return engine

    def get_generator(self) -> Generator:
        """
        Creates and returns a Generator object that yields a local database connection.

        Returns:
            Generator: Yields a local database connection.
        """
        sessionmaker_kwargs = {"autocommit": False, "autoflush": False, "bind": self.engine}
        session = sessionmaker(**sessionmaker_kwargs)
        db = session()

        try: yield db
        finally: db.close()

    def initialize_database(self):
        """
        Initialize the database, and create all tables.
        """
        Base.metadata.create_all(bind=self.engine)


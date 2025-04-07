from typing import Generator
from sqlalchemy import create_engine 
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker 
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Database:
    def __init__(self, database_uri: str, echo: bool = False):
        """
        Args:
            database_uri (str): URI for the database to connect to.
            echo (bool): Whether to echo SQL statements to the console for debugging.
                         Defaults to False.
        """
        self._engine = self._create_engine(database_uri, echo)
    
    def _create_engine(self, databse_uri: str, echo: bool) -> Engine:
        """
        Returns:
            Engine: Instance of SQLAlchemy Engine that can be used to interact with 
                    the database.
        """
        connect_args = {"check_same_thread": False} # Required for SQLite
        engine = create_engine(databse_uri, echo=echo, connect_args=connect_args)
        return engine

    def get_db(self) -> Generator[Session, None, None]:
        """
        Yields:
            sqlalchemy.orm.Session: A new database session instance bound to the engine.
                                    Automatically closed when the context exits.
            
        """
        sessionmaker_kwargs = {"autocommit": False, "autoflush": False, "bind": self._engine}
        session = sessionmaker(**sessionmaker_kwargs)
        db = session()

        try:
            yield db
        finally:
            db.close()

    def initalize_tables(self):
        Base.metadata.create_all(bind=self._engine)


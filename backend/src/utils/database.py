from typing import Any, Dict, Generator
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

Base = declarative_base()

class Database:
    def __init__(self, database_uri: str, echo: bool = False):
        """
        Args:
            database_uri (str): URI for the database to connect to.
            echo (bool): Whether to echo SQL statements to the console, for debugging purposes.
                Defaults to False.
        """
        self._engine = self._create_engine(database_uri, echo)
        self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine)

    def _create_engine(self, database_uri: str, echo: bool) -> Engine:
        """
        Returns:
            sqlalchemy.Engine: Instance of SQLAlchemy Engine that can be used to interact with 
                the database.
        """
        connect_args: Dict[str, Any] = {}

        # check_same_thread is specific to sqlite
        if database_uri.startswith("sqlite"):
            connect_args["check_same_thread"] = False

        engine = create_engine(database_uri, echo=echo, connect_args=connect_args)
        return engine

    def get_db(self) -> Generator[Session, None, None]:
        """
        Yields:
            sqlalchemy.orm.Session: A database session, bound to the engine.
                Automatically closed when the context exits.
        """
        db = self._session_factory()
        try: yield db
        finally: db.close()

    def get_session(self) -> Session:
        """
        For use within a 'with' statement for automatic cleanup.

        Returns:
            sqlalchemy.orm.Session: A database session, bound to the engine.
        """
        return self._session_factory()

    def initialize_tables(self):
        """Creates all tables defined in the Base metadata"""
        Base.metadata.create_all(bind=self._engine)


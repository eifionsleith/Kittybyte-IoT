import sys
import os

from pydantic import ValidationError
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.crud.user import UserConflictError, user_crud_interface
from src.schemas.user import UserCreate
from src.utils.database import Database
from src.utils.config import get_config

def print_usage():
    print("Usage:\npython create_superuser.py {email} {username} {password}\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print_usage()
        raise SystemExit("Incorrect number of arguments. Expecting 3 arguments.")
    
    settings = get_config(".env.dev")
    database = Database(settings.db.uri, settings.db.echo_all)
    database.initialize_tables()

    try:
        user_create = UserCreate(email=sys.argv[1], 
                                 username=sys.argv[2],
                                 password=sys.argv[3])
        with database.get_session() as db:
            user_crud_interface.validate_creation_schema(db, user_create)
            user = user_crud_interface.create(db, user_create)
            user = user_crud_interface.set_is_superuser(db, user, True)

    except ValidationError:
        print_usage()
        raise SystemExit("Invalid arguments. Expecting an email as first argument.")
    except UserConflictError:
        print_usage()
        raise SystemExit("Username as Email must be unique. Such user already exists in database.")


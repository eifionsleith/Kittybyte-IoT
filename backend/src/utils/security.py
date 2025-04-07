from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from passlib.context import CryptContext


_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plaintext_password: str, hashed_password: str) -> bool:
    """
    Args:
        plaintext_password (str): A plaintext password to compare.
        hashed_password (str): A hashed password to compare against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return _PWD_CONTEXT.verify(plaintext_password, hashed_password)

def get_password_hash(plaintext_password: str) -> str:
    """
    Args:
        plaintext_password (str): Password string to create hash for.

    Returns:
        str: Hashed represenation for the given string.
    """
    return _PWD_CONTEXT.hash(plaintext_password)

def create_jwt(subject: str | Any,
               expires_delta: timedelta,
               jwt_secret: str,
               jwt_algorithm: str) -> str:
    """
    Args:
        subject (str): JWT Sub field - see the JWT spec for more details.
        expires_delta (timedelta): Time for this token to remain valid.
        jwt_secret (str): Secret key used to generate this token.
        jwt_algorithm (str): Cryptographic algorithm used to generate this token. Example: "HS256"
    
    Returns:
        str: Encoded string containing the JWT Token.
    """
    expiry = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": str(subject), "exp": expiry}  # Sub must be str to decode
    encoded = jwt.encode(to_encode, jwt_secret, jwt_algorithm)
    return encoded


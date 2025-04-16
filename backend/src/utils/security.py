import jwt
from typing import Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext


_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plaintext_password: str, password_hash: str) -> bool:
    """
    Verifies a plaintext password against a password hash.

    Args:
        plaintext_password (str): Plaintext password to compare.
        password_hash (str): Password hash to compare against.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return _PWD_CONTEXT.verify(plaintext_password, password_hash)

def get_password_hash(plaintext_password: str) -> str:
    """
    Generates a hash for an input password.

    Args:
        plaintext_password (str): Password to generate hash for.

    Returns:
        str: Valid hash for the provided password.
    """
    return _PWD_CONTEXT.hash(plaintext_password)

def create_jwt(subject: str | Any,
               expires_delta: timedelta,
               jwt_secret: str,
               jwt_algorithm: str) -> str:
    """
    Generates a JWT access token for the provided paramaters.

    Args:
        subject (str): JWT Sub field, see JWT documentation for more details. Typically User UUID.
        expires_delta (timedelta): Time until token is to expire, as timedelta.
        jwt_secret (str): Secret key used to generate this token.
        jwt_algorithm (str): Cryptographic algorithm to generate this token. Example: "HS256"

    Returns:
        str: Encoded string containing the JWT access token.
    """
    exp = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": str(subject), "exp": exp}  # sub must be a string to decode, will quietly fail otherwise
    encoded = jwt.encode(to_encode, jwt_secret, jwt_algorithm)
    return encoded


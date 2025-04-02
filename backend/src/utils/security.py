from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

_PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plaintext_password: str, hashed_password: str) -> bool:
    """
    Compares a hashed password and a plaintext string, and
    returns True if they match, otherwise returns False.

    Args:
        plaintext_password (str): Plaintext represenation of a password.
        hashed_password (str): Hashed represenation of a password.

    Returns:
        bool: True if passwords match, False otherwise.
    """
    return _PWD_CONTEXT.verify(plaintext_password, hashed_password)

def get_password_hash(plaintext_password: str) -> str:
    """
    Takes a plaintext string, and returns a hshed represenation.

    Args:
        plaintext_password (str): String to hash.

    Returns:
        str: Hash for the given string.
    """
    return _PWD_CONTEXT.hash(plaintext_password)

def create_jwt(
        subject: str | Any,
        expires_delta: timedelta,
        jwt_secret: str, 
        jwt_algorithm: str) -> str:
    """
    Creates a JWT Access Token for the given subject.
    See the JWT spec for more details.

    Args:
        subject (str): JWT Sub field, typically identifier for the user.
        expires_delta (timedelta): Time for the token to remain valid.

    Returns:
        str: Encoded JWT Access Token that can be safely issued to the end user.
    """
    expiry = datetime.now(timezone.utc) + expires_delta
    to_encode = { "sub": str(subject), "exp": expiry }
    encoded = jwt.encode(to_encode, jwt_secret, jwt_algorithm)
    return encoded


import jwt
from typing import Any
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

from utils.settings import get_settings

class Security:
    _PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(plaintext_password: str, hashed_password: str) -> bool:
        """
        Compares a hashed and plaintext representation of a given password, returning True if they match.

        Args:
            plaintext_password (str): Plaintext representation of a password, typically user input.
            hashed_password (str): Hashed representation of a password, typically from database.

        Returns:
            bool: True if passwords match, False otherwise.
        """
        return Security._PWD_CONTEXT.verify(plaintext_password, hashed_password)

    @staticmethod
    def get_password_hash(plaintext_password: str) -> str:
        """
        Takes a plaintext password, and returns a valid hashed representation.

        Args:
            plaintext_password (str): Plaintext password to hash.

        Returns:
            str: Hashed representation of the given password.
        """
        return Security._PWD_CONTEXT.hash(plaintext_password)

    @staticmethod
    def create_jwt(subject: str | Any, expires_delta: timedelta) -> str:
        """
        Creates a JWT Access Token for the given subject.
        See the JWT spec for more details.

        Args:
            subject (str): JWT sub field, identifier for the user this JWT is issued for.
            expires_delta (timedelta): How long the JWT should be valid for.

        Returns:
            str: Encoded JWT Access Token that can be issued to the end user.
        """
        app_settings = get_settings()
        jwt_secret_key = app_settings.jwt_secret
        algorithm = app_settings.jwt_algorithm
        expiry = datetime.now(timezone.utc) + expires_delta
        # Note that subject must be typecasted to string, otherwise JWT cannot be decoded.
        to_encode = {"sub": str(subject), "exp": expiry} 
        encoded = jwt.encode(to_encode, jwt_secret_key, algorithm)
        return encoded


import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plaintext_password: str, hashed_password: str) -> bool:
    """
    Compares a hashed and plaintext password, returning a boolean whether they match or not.
    """
    return pwd_context.verify(plaintext_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Takes a plaintext password and returns a corresponding hash.
    """
    return pwd_context.hash(password)

def create_jwt(subject: str, expires_delta: timedelta) -> str:
    """
    Creates a JWT Access Token for a given subject and expiry.
    See JWT Spec for more details.
    """
    expiry = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expiry}
    encoded = jwt.encode(to_encode, config.jwt_secret_key, algorithm=config.jwt_algorithm)
    return encoded


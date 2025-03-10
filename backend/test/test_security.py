import jwt
from datetime import datetime, timedelta, timezone
from security import create_jwt, get_password_hash, verify_password
from config import config

def test_password_hash():
    password = "s3cur3!"
    hash = get_password_hash(password)
    assert password not in hash

def test_verify_password():
    password = "s3cur3@@@"
    hash = get_password_hash(password)
    assert verify_password(password, hash)

def test_create_jwt():
    subject = "usr111"
    expires_delta = timedelta(minutes=15)

    token = create_jwt(subject, expires_delta)
    assert token
    assert isinstance(token, str)

    decoded = jwt.decode(token, config.jwt_secret_key, algorithms=[config.jwt_algorithm])
    assert decoded
    assert decoded["sub"] == subject
    assert decoded["exp"] > datetime.now(timezone.utc).timestamp()
    

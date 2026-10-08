import uuid
import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from app.core.config import settings

# Password hasher supporting both Argon2 (modern standard) and Bcrypt
password_hash = PasswordHash((Argon2Hasher(), BcryptHasher()))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against the stored hash."""
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a secure salt-and-hash string for a plaintext password."""
    return password_hash.hash(password)

def create_access_token(subject: str) -> str:
    """Generates a short-lived access token with type='access' claim."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(subject),
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    """
    Returns (token_string, jti, expire_datetime).
    We persist jti and expire_datetime in the database.
    """
    jti = str(uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(subject),
        "jti": jti,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, jti, expire

def decode_refresh_token(token: str) -> dict | None:
    """Decodes token and returns payload dict if valid, else None."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except (jwt.PyJWTError, ValueError):
        return None

def create_password_reset_token(email: str) -> str:
    """Generates a 15-minute token specifically for resetting passwords."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "sub": email,
        "type": "password_reset",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_password_reset_token(token: str) -> str | None:
    """Decodes token and returns email if valid, otherwise None."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except (jwt.PyJWTError, ValueError):
        return None

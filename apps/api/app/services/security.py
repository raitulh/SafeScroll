from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from app.config import settings

ph = PasswordHasher()

class AuthError(Exception):
    pass

def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters.")
    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False

def _encode(payload: dict, expires: timedelta) -> str:
    now = datetime.now(timezone.utc)
    body = {**payload, "iat": now, "exp": now + expires}
    return jwt.encode(body, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def create_access_token(user_id: int) -> str:
    return _encode({"sub": str(user_id), "type": "access"}, timedelta(minutes=settings.access_token_minutes))

def create_refresh_token(user_id: int) -> str:
    nonce = secrets.token_urlsafe(32)
    return _encode({"sub": str(user_id), "type": "refresh", "jti": nonce}, timedelta(days=settings.refresh_token_days))

def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid or expired token.") from exc
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise AuthError("Invalid token type.")
    return payload

def token_hash(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

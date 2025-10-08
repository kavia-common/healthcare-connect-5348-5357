from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from passlib.context import CryptContext
from fastapi.security import HTTPBearer

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer(auto_error=True)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed value."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plaintext password for storage."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def create_access_token(subject: Dict[str, Any]) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Claims to include in the token (e.g., {'sub': user_id, 'email': ..., 'role': ...})

    Returns:
        str: Signed JWT.
    """
    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    now = datetime.now(tz=timezone.utc)
    to_encode = subject.copy()
    to_encode.update({"exp": now + timedelta(minutes=expire_minutes), "iat": now, "nbf": now})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


# PUBLIC_INTERFACE
def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a signed JWT access token.

    Args:
        token: The bearer token string.

    Returns:
        dict: Decoded claims.

    Raises:
        jwt.PyJWTError: If token is invalid or expired.
    """
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    return payload

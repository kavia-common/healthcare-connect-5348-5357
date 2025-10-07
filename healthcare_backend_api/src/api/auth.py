"""Authentication helpers: password hashing and JWT utilities."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

# Load environment variables from .env
load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "change_me_in_prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
# Allow small clock skew to reduce spurious 401s due to device time drift
JWT_CLOCK_SKEW_SECONDS = int(os.getenv("JWT_CLOCK_SKEW_SECONDS", "30"))


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hashed counterpart."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token with an expiration and issued-at claim.

    Args:
        data: Claims to include in the token (will be copied).
        expires_delta: Optional timedelta to override token duration.

    Returns:
        A signed JWT string.
    """
    to_encode = data.copy()
    now = datetime.now(tz=timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES))
    # Include standard registered claims: exp (expiry) and iat (issued at)
    to_encode.update({"exp": expire, "iat": int(now.timestamp())})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


# PUBLIC_INTERFACE
def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT, returning its claims.

    Raises:
        JWTError: if the token is invalid or expired.
    """
    # Add leeway for clock skew configurable via env
    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={"leeway": JWT_CLOCK_SKEW_SECONDS},
    )
    return payload

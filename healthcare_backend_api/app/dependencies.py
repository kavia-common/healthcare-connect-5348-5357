from typing import Annotated, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.database import get_db_from_app
from app.core.security import http_bearer, decode_access_token


# PUBLIC_INTERFACE
def get_db(request: Request):
    """Yield the active database connection from app state.

    Args:
        request: FastAPI request object.

    Returns:
        AsyncIOMotorDatabase: Mongo database instance.
    """
    return get_db_from_app(request.app)


# PUBLIC_INTERFACE
async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> Dict:
    """Resolve the current user from bearer token and fetch from DB.

    Args:
        request: FastAPI request.
        credentials: Authorization header with Bearer token.

    Returns:
        dict: Sanitized user document.

    Raises:
        HTTPException: If token invalid or user not found.
    """
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    db = get_db_from_app(request.app)
    user = await db["users"].find_one({"_id": user_id})  # we store string IDs in users
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user.pop("hashed_password", None)
    return user


# PUBLIC_INTERFACE
def require_roles(*roles: str):
    """Dependency factory to enforce required user roles."""

    async def _checker(current_user: Annotated[Dict, Depends(get_current_user)]) -> Dict:
        role = current_user.get("role")
        if roles and role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return _checker

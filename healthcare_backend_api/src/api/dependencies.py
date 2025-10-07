"""FastAPI dependencies for authentication and authorization."""

from typing import Any, Callable, Dict, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from src.api.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get the current user claims from a Bearer token.

    Returns:
        A dictionary of user claims (e.g., sub, email, role).

    Raises:
        HTTPException: 401 if token is invalid or missing.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload is None or "sub" not in payload:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception


# PUBLIC_INTERFACE
def role_required(allowed_roles: List[str]) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Return a dependency function that ensures the current user has one of the allowed roles.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(role_required(["admin"]))])
        async def admin_only_endpoint(...):
            ...

    Args:
        allowed_roles: List of roles that are authorized for the endpoint.

    Returns:
        A dependency function that either returns the user claims or raises HTTP 403.
    """

    def _dependency(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        role = user.get("role")
        if allowed_roles and role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _dependency

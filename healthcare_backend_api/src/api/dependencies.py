"""FastAPI dependencies for authentication and authorization."""

from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError

from src.api.auth import decode_access_token

# Allow OAuth2 extraction but do not auto-raise to support fallbacks below
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# PUBLIC_INTERFACE
def get_current_user(request: Request, token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get the current user claims from a Bearer token.

    Tries multiple sources for better client compatibility:
    - Authorization: Bearer <token> (standard)
    - X-Auth-Token: <token> (fallback header)
    - token=<token> (query param fallback)

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

    # Fallback to raw Authorization header if oauth2 didn't extract a token
    if not token:
        auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
        if auth_header:
            scheme, param = get_authorization_scheme_param(auth_header)
            if scheme and scheme.lower() == "bearer" and param:
                token = param

    # Additional fallbacks: custom header or query param
    if not token:
        token = request.headers.get("X-Auth-Token") or request.query_params.get("token")

    if not token:
        # No token supplied in any supported location
        raise credentials_exception

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

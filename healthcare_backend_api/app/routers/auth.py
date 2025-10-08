from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import TokenResponse, UserCreate, UserLogin, UserPublic
from app.utils.mappers import to_public_id
from app.dependencies import get_db

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=TokenResponse,
    summary="Register a new user",
    description="Create a new user account and return an access token.",
)
async def register_user(payload: UserCreate, request: Request, db=Depends(get_db)) -> TokenResponse:
    """Register a new user.

    Args:
        payload: User creation payload.
        request: The request object.
        db: Injected MongoDB database.

    Returns:
        TokenResponse: JWT token and created user.

    Raises:
        HTTPException: If user already exists.
    """
    email = payload.email.lower()
    existing = await db["users"].find_one({"email": email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_doc: Dict[str, Any] = {
        "_id": email,  # use email as unique string ID for simplicity
        "email": email,
        "full_name": payload.full_name,
        "role": payload.role,
        "hashed_password": get_password_hash(payload.password),
    }
    await db["users"].insert_one(user_doc)

    public_user = UserPublic(**to_public_id(user_doc) | {"id": user_doc["_id"]})
    token = create_access_token({"sub": user_doc["_id"], "email": email, "role": payload.role})
    return TokenResponse(access_token=token, token_type="bearer", user=public_user)


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and get access token",
    description="Authenticate using email/password and receive a bearer token.",
)
async def login_user(payload: UserLogin, request: Request, db=Depends(get_db)) -> TokenResponse:
    """Authenticate a user with email and password.

    Args:
        payload: Login payload (email and password).
        request: The request object.
        db: Injected MongoDB database.

    Returns:
        TokenResponse: JWT token and user info.

    Raises:
        HTTPException: If credentials are invalid.
    """
    email = payload.email.lower()
    user: Optional[Dict[str, Any]] = await db["users"].find_one({"email": email})
    if not user or not verify_password(payload.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    public_user = UserPublic(**to_public_id(user) | {"id": user["_id"]})
    token = create_access_token({"sub": user["_id"], "email": email, "role": user.get("role")})
    return TokenResponse(access_token=token, token_type="bearer", user=public_user)

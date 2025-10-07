"""Authentication router: login and registration endpoints."""

from datetime import timedelta
from typing import Any, Dict

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth import (
    ACCESS_TOKEN_EXPIRES_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)
from src.api.db import get_db
from src.api.dependencies import get_current_user
from src.api.models import Token, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["Auth"])


def _public_user_from_doc(doc: Dict[str, Any]) -> UserPublic:
    """Transform a user MongoDB document into a public model."""
    return UserPublic(
        id=str(doc["_id"]),
        email=doc["email"],
        full_name=doc.get("full_name"),
        role=doc.get("role", "patient"),
    )


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate a user with email and password and return a JWT token.",
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Invalid credentials"},
    },
)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Validate user credentials and issue a JWT bearer token.

    Uses OAuth2PasswordRequestForm where 'username' is the user's email address.
    """
    db = await get_db()
    user = await db["users"].find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    token = create_access_token(
        data={"sub": str(user["_id"]), "email": user["email"], "role": user.get("role", "patient")},
        expires_delta=access_token_expires,
    )
    return Token(access_token=token, token_type="bearer")


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserPublic,
    status_code=201,
    summary="Register",
    description="Create a new user account with role-based profile initialization.",
    responses={
        201: {"description": "User registered"},
        400: {"description": "Email already registered"},
    },
)
async def register_user(payload: UserCreate) -> UserPublic:
    """Register a new user, hashing the password and creating role-specific profiles."""
    db = await get_db()
    existing = await db["users"].find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    doc: Dict[str, Any] = {
        "email": payload.email,
        "full_name": payload.full_name,
        "role": payload.role,
        "hashed_password": get_password_hash(payload.password),
    }
    result = await db["users"].insert_one(doc)
    user_id = result.inserted_id

    # Initialize role-specific profile
    if payload.role == "patient":
        await db["patients"].insert_one(
            {"user_id": str(user_id), "age": None, "gender": None, "address": None}
        )
    elif payload.role == "doctor":
        await db["doctors"].insert_one(
            {"user_id": str(user_id), "specialty": None, "bio": None}
        )

    # Fetch inserted user to ensure full representation
    created = await db["users"].find_one({"_id": user_id})
    return _public_user_from_doc(created)


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=UserPublic,
    summary="Current user",
    description="Return the current authenticated user's public profile.",
)
async def me(user_claims: Dict[str, Any] = Depends(get_current_user)) -> UserPublic:
    """Return information about the authenticated user based on the token claims."""
    db = await get_db()
    try:
        oid = ObjectId(user_claims["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    doc = await db["users"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return _public_user_from_doc(doc)

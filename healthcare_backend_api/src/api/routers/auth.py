"""Authentication router: login and registration endpoints (scaffold)."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth import ACCESS_TOKEN_EXPIRES_MINUTES, create_access_token
from src.api.models import Token, UserCreate, UserPublic

router = APIRouter(prefix="/auth", tags=["Auth"])


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
    """Temporary scaffold: issue a JWT token without verifying credentials.

    NOTE: This is a placeholder and must be replaced with real credential validation.
    """
    # Scaffold-only: generate a token using the provided username as subject.
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    token = create_access_token(data={"sub": form_data.username, "role": "patient"}, expires_delta=access_token_expires)
    return Token(access_token=token, token_type="bearer")


# PUBLIC_INTERFACE
@router.post(
    "/register",
    response_model=UserPublic,
    status_code=201,
    summary="Register",
    description="Create a new user account (scaffold; not implemented).",
    responses={
        201: {"description": "User registered"},
        501: {"description": "Not implemented"},
    },
)
async def register_user(payload: UserCreate) -> UserPublic:
    """Scaffold placeholder for user registration - returns 501 Not Implemented."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Unique email address")
    full_name: Optional[str] = Field(None, description="Full name of the user")
    role: Literal["patient", "doctor", "admin"] = Field(..., description="Role of the user")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password for the new account")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email to login")
    password: str = Field(..., description="Password to login")


class UserPublic(UserBase):
    id: str = Field(..., description="User identifier")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Type of token")
    user: UserPublic = Field(..., description="Authenticated user information")

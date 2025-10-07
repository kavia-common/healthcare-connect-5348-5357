"""Consultations router (scaffold)."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user
from src.api.models import Consultation

router = APIRouter(prefix="/consultations", tags=["Consultations"])


# PUBLIC_INTERFACE
@router.get(
    "",
    summary="List consultations",
    description="List consultations for the current user. Placeholder endpoint returning 501 until implemented.",
    responses={501: {"description": "Not implemented"}},
)
async def list_consultations(_: dict = Depends(get_current_user)):
    """List consultations - scaffold placeholder."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=Consultation,
    summary="Create consultation",
    description="Create a new consultation. Placeholder endpoint returning 501 until implemented.",
    responses={501: {"description": "Not implemented"}},
)
async def create_consultation(_: dict = Depends(get_current_user)):
    """Create consultation - scaffold placeholder."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

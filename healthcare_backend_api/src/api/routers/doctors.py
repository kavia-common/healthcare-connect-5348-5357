"""Doctors router (scaffold)."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import role_required
from src.api.models import Doctor

router = APIRouter(prefix="/doctors", tags=["Doctors"])


# PUBLIC_INTERFACE
@router.get(
    "",
    summary="List doctors",
    description="List doctors. Placeholder endpoint returning 501 until implemented.",
    responses={501: {"description": "Not implemented"}},
)
async def list_doctors(_: dict = Depends(role_required(["admin", "patient"]))):
    """List doctors - scaffold placeholder."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=Doctor,
    summary="Create doctor",
    description="Create a new doctor record. Placeholder endpoint returning 501 until implemented.",
    responses={501: {"description": "Not implemented"}},
)
async def create_doctor(_: dict = Depends(role_required(["admin"]))):
    """Create doctor - scaffold placeholder."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

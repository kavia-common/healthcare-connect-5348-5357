"""Patients router (scaffold)."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user, role_required
from src.api.models import Patient

router = APIRouter(prefix="/patients", tags=["Patients"])


# PUBLIC_INTERFACE
@router.get(
    "",
    summary="List patients",
    description="List patients. Placeholder endpoint returning 501 until implemented.",
    responses={501: {"description": "Not implemented"}},
)
async def list_patients(_: dict = Depends(role_required(["admin", "doctor"]))):
    """List patients - scaffold placeholder."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=Patient,
    summary="Create patient",
    description="Create a new patient record. Placeholder endpoint returning 501 until implemented.",
    responses={501: {"description": "Not implemented"}},
)
async def create_patient(_: dict = Depends(get_current_user)) -> Patient:
    """Create patient - scaffold placeholder."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

"""Medical records router (scaffold)."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import role_required
from src.api.models import MedicalRecord

router = APIRouter(prefix="/medical_records", tags=["Medical Records"])


# PUBLIC_INTERFACE
@router.get(
    "",
    summary="List medical records",
    description="List medical records accessible to the current user. Placeholder endpoint returning 501 until implemented.",
    responses={501: {"description": "Not implemented"}},
)
async def list_medical_records(_: dict = Depends(role_required(["admin", "doctor", "patient"]))):
    """List medical records - scaffold placeholder."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=MedicalRecord,
    summary="Create medical record",
    description="Create a new medical record. Placeholder endpoint returning 501 until implemented.",
    responses={501: {"description": "Not implemented"}},
)
async def create_medical_record(_: dict = Depends(role_required(["admin", "doctor"]))):
    """Create medical record - scaffold placeholder."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")

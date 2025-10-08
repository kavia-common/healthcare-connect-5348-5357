from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.dependencies import get_current_user, get_db
from app.models.medical_record import MedicalRecordCreate, MedicalRecordPublic, MedicalRecordUpdate
from app.utils.mappers import to_public_id

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=MedicalRecordPublic,
    summary="Create medical record",
    description="Create a new medical record (doctor only).",
)
async def create_medical_record(
    payload: MedicalRecordCreate,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> MedicalRecordPublic:
    """Create a new medical record. Only users with the 'doctor' role are allowed."""
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can create medical records")

    doc = payload.model_dump()
    doc["_id"] = f"mrec::{payload.patient_id}::{payload.created_at.isoformat()}"
    await db["medical_records"].insert_one(doc)
    return MedicalRecordPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[MedicalRecordPublic],
    summary="List medical records",
    description="List medical records filtered by patient_id (patients can only view their own).",
)
async def list_medical_records(
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    patient_id: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> List[MedicalRecordPublic]:
    """List medical records with optional filtering by patient_id."""
    query = {}
    if patient_id:
        query["patient_id"] = patient_id

    # Patients can only see their own records
    if current_user["role"] == "patient":
        # Ensure patient profile
        patient = await db["patients"].find_one({"user_id": current_user["id"]})
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
        query["patient_id"] = patient["_id"]

    cursor = db["medical_records"].find(query, skip=skip, limit=limit, sort=[("created_at", -1)])
    items = [to_public_id(doc) | {"id": doc["_id"]} async for doc in cursor]
    return [MedicalRecordPublic(**it) for it in items]


# PUBLIC_INTERFACE
@router.get(
    "/{record_id}",
    response_model=MedicalRecordPublic,
    summary="Get medical record by id",
    description="Retrieve a medical record by identifier.",
)
async def get_medical_record(
    record_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> MedicalRecordPublic:
    """Get a medical record by ID."""
    doc = await db["medical_records"].find_one({"_id": record_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")

    if current_user["role"] == "patient":
        patient = await db["patients"].find_one({"user_id": current_user["id"]})
        if not patient or doc.get("patient_id") != patient["_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this record")

    return MedicalRecordPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.put(
    "/{record_id}",
    response_model=MedicalRecordPublic,
    summary="Update medical record",
    description="Update fields on a medical record (doctor only).",
)
async def update_medical_record(
    record_id: str,
    payload: MedicalRecordUpdate,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> MedicalRecordPublic:
    """Update a medical record. Only doctors can update."""
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can update medical records")

    doc = await db["medical_records"].find_one({"_id": record_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")

    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if update:
        await db["medical_records"].update_one({"_id": record_id}, {"$set": update})
        doc.update(update)
    return MedicalRecordPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.delete(
    "/{record_id}",
    status_code=204,
    summary="Delete medical record",
    description="Delete a medical record (doctor or admin).",
)
async def delete_medical_record(
    record_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Delete a medical record. Allowed for doctors and admins."""
    if current_user["role"] not in {"doctor", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors/admins can delete records")

    doc = await db["medical_records"].find_one({"_id": record_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medical record not found")

    await db["medical_records"].delete_one({"_id": record_id})
    return None

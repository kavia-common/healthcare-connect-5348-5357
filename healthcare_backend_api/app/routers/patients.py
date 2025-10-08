from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.dependencies import get_current_user, get_db, require_roles
from app.models.patient import PatientCreate, PatientPublic, PatientUpdate
from app.utils.mappers import to_public_id

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=PatientPublic,
    summary="Create patient profile",
    description="Create a patient profile for the authenticated patient user.",
)
async def create_patient(
    payload: PatientCreate,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(require_roles("patient"))] = None,
) -> PatientPublic:
    """Create a patient profile for the current authenticated patient."""
    # Enforce that user_id in payload matches authenticated user (if provided)
    if payload.user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id must match the authenticated user")

    existing = await db["patients"].find_one({"user_id": payload.user_id})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient profile already exists")

    doc = payload.model_dump()
    # Use a string ID: patient::<user_id>
    doc["_id"] = f"patient::{payload.user_id}"
    await db["patients"].insert_one(doc)
    return PatientPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=PatientPublic,
    summary="Get my patient profile",
    description="Retrieve the patient profile associated with the authenticated patient user.",
)
async def get_my_patient_profile(
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(require_roles("patient"))] = None,
) -> PatientPublic:
    """Get the current patient's profile."""
    doc = await db["patients"].find_one({"user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found")
    return PatientPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[PatientPublic],
    summary="List patients",
    description="List patient profiles with pagination.",
)
async def list_patients(
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> List[PatientPublic]:
    """List patient profiles with optional pagination."""
    cursor = db["patients"].find({}, skip=skip, limit=limit)
    items = [to_public_id(doc) | {"id": doc["_id"]} async for doc in cursor]
    return [PatientPublic(**it) for it in items]


# PUBLIC_INTERFACE
@router.get(
    "/{patient_id}",
    response_model=PatientPublic,
    summary="Get patient by id",
    description="Retrieve a patient profile by identifier.",
)
async def get_patient_by_id(
    patient_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> PatientPublic:
    """Get a patient profile by ID."""
    doc = await db["patients"].find_one({"_id": patient_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return PatientPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.put(
    "/{patient_id}",
    response_model=PatientPublic,
    summary="Update patient profile",
    description="Update fields on a patient profile.",
)
async def update_patient(
    patient_id: str,
    payload: PatientUpdate,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> PatientPublic:
    """Update a patient profile."""
    doc = await db["patients"].find_one({"_id": patient_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

    # Allow update if owner or doctor/admin
    if current_user["role"] == "patient" and doc.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify others' profiles")

    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if update:
        await db["patients"].update_one({"_id": patient_id}, {"$set": update})
        doc.update(update)
    return PatientPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.delete(
    "/{patient_id}",
    status_code=204,
    summary="Delete patient profile",
    description="Delete a patient profile by identifier.",
)
async def delete_patient(
    patient_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Delete a patient profile."""
    doc = await db["patients"].find_one({"_id": patient_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    if current_user["role"] == "patient" and doc.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete others' profiles")

    await db["patients"].delete_one({"_id": patient_id})
    return None

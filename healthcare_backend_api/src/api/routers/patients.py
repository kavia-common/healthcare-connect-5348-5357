"""Patients router with CRUD operations and RBAC."""

from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.api.db import get_db
from src.api.dependencies import get_current_user, role_required
from src.api.models import Patient, PatientCreate, PatientUpdate

router = APIRouter(prefix="/patients", tags=["Patients"])


def _patient_from_doc(doc: Dict[str, Any]) -> Patient:
    """Map a MongoDB patient document to Patient model."""
    return Patient(
        id=str(doc.get("_id") or doc.get("id")),
        user_id=doc["user_id"],
        age=doc.get("age"),
        gender=doc.get("gender"),
        address=doc.get("address"),
    )


async def _assert_patient_owner_or_admin(
    patient_doc: Dict[str, Any], user_claims: Dict[str, Any]
) -> None:
    """Raise 403 if the user is not allowed to act on this patient doc."""
    role = user_claims.get("role")
    if role == "admin":
        return
    if role == "patient" and patient_doc.get("user_id") == user_claims.get("sub"):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[Patient],
    summary="List patients",
    description="List all patients. Only accessible to admins and doctors.",
)
async def list_patients(_: Dict[str, Any] = Depends(role_required(["admin", "doctor"]))) -> List[Patient]:
    """Return all patient profiles."""
    db = await get_db()
    cursor = db["patients"].find({})
    results = [ _patient_from_doc(doc) async for doc in cursor ]
    return results


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=Patient,
    status_code=201,
    summary="Create patient",
    description="Create a new patient profile. Patients can create their own; admins can create for any user.",
)
async def create_patient(
    payload: PatientCreate,
    user_claims: Dict[str, Any] = Depends(get_current_user),
) -> Patient:
    """Create a patient profile with RBAC rules."""
    db = await get_db()
    role = user_claims.get("role")

    user_id: Optional[str] = payload.user_id
    if role == "patient":
        user_id = user_claims["sub"]  # patients can only create their own profile
    elif role == "admin":
        if not user_id:
            raise HTTPException(status_code=400, detail="user_id is required for admin-created profiles")
    else:
        raise HTTPException(status_code=403, detail="Only patients and admins can create patient profiles")

    doc: Dict[str, Any] = {
        "user_id": user_id,
        "age": payload.age,
        "gender": payload.gender,
        "address": payload.address,
    }
    result = await db["patients"].insert_one(doc)
    created = await db["patients"].find_one({"_id": result.inserted_id})
    return _patient_from_doc(created)


# PUBLIC_INTERFACE
@router.get(
    "/{patient_id}",
    response_model=Patient,
    summary="Get patient",
    description="Retrieve a patient profile by id. Admins/doctors can access any; patients only their own.",
)
async def get_patient(
    patient_id: str = Path(..., description="Patient document id"),
    user_claims: Dict[str, Any] = Depends(get_current_user),
) -> Patient:
    """Get a specific patient profile with RBAC enforcement."""
    db = await get_db()
    try:
        oid = ObjectId(patient_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Patient not found")

    doc = await db["patients"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Patient not found")

    # RBAC checks
    role = user_claims.get("role")
    if role == "admin" or role == "doctor" or (role == "patient" and doc.get("user_id") == user_claims.get("sub")):
        return _patient_from_doc(doc)
    raise HTTPException(status_code=403, detail="Insufficient permissions")


# PUBLIC_INTERFACE
@router.patch(
    "/{patient_id}",
    response_model=Patient,
    summary="Update patient",
    description="Update a patient profile. Admins or the patient owner can update.",
)
async def update_patient(
    patient_id: str,
    payload: PatientUpdate,
    user_claims: Dict[str, Any] = Depends(get_current_user),
) -> Patient:
    """Update patient fields with partial payload."""
    db = await get_db()
    try:
        oid = ObjectId(patient_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Patient not found")

    doc = await db["patients"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Patient not found")

    await _assert_patient_owner_or_admin(doc, user_claims)

    updates: Dict[str, Any] = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if updates:
        await db["patients"].update_one({"_id": oid}, {"$set": updates})
    updated = await db["patients"].find_one({"_id": oid})
    return _patient_from_doc(updated)


# PUBLIC_INTERFACE
@router.delete(
    "/{patient_id}",
    status_code=204,
    summary="Delete patient",
    description="Delete a patient profile. Admin only.",
)
async def delete_patient(
    patient_id: str,
    _: Dict[str, Any] = Depends(role_required(["admin"])),
) -> None:
    """Delete a patient profile (admin only)."""
    db = await get_db()
    try:
        oid = ObjectId(patient_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = await db["patients"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Patient not found")

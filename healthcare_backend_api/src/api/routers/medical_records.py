"""Medical records router with CRUD operations and RBAC."""

from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from src.api.db import get_db
from src.api.dependencies import get_current_user_strict, role_required_strict
from src.api.models import MedicalRecord, MedicalRecordCreate, MedicalRecordUpdate

router = APIRouter(prefix="/medical_records", tags=["Medical Records"])


def _record_from_doc(doc: Dict[str, Any]) -> MedicalRecord:
    """Map a MongoDB medical record document to MedicalRecord model."""
    return MedicalRecord(
        id=str(doc.get("_id") or doc.get("id")),
        patient_id=doc["patient_id"],
        entries=list(doc.get("entries", [])),
    )


async def _get_patient_id_for_user(db, user_id: str) -> Optional[str]:
    patient = await db["patients"].find_one({"user_id": user_id})
    return str(patient["_id"]) if patient else None


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[MedicalRecord],
    summary="List medical records",
    description="List medical records accessible to the current user. Admins: all. Doctors: require patient_id filter. Patients: their own.",
)
async def list_medical_records(
    patient_id: Optional[str] = Query(None, description="Filter by patient id (required for doctors)"),
    user_claims: Dict[str, Any] = Depends(get_current_user_strict),
) -> List[MedicalRecord]:
    """Return medical records based on role and provided filters."""
    db = await get_db()
    role = user_claims.get("role")
    query: Dict[str, Any] = {}

    if role == "admin":
        if patient_id:
            query["patient_id"] = patient_id
    elif role == "doctor":
        if not patient_id:
            raise HTTPException(status_code=400, detail="patient_id is required for doctors")
        query["patient_id"] = patient_id
    else:  # patient
        own_patient_id = await _get_patient_id_for_user(db, user_claims["sub"])
        if not own_patient_id:
            return []
        query["patient_id"] = own_patient_id

    cursor = db["medical_records"].find(query)
    return [_record_from_doc(doc) async for doc in cursor]


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=MedicalRecord,
    status_code=201,
    summary="Create medical record",
    description="Create a new medical record. Admins and doctors only.",
)
async def create_medical_record(
    payload: MedicalRecordCreate,
    _: Dict[str, Any] = Depends(role_required_strict(["admin", "doctor"])),
) -> MedicalRecord:
    """Create a medical record for a patient."""
    db = await get_db()
    try:
        poid = ObjectId(payload.patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id")

    patient = await db["patients"].find_one({"_id": poid})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    doc: Dict[str, Any] = {"patient_id": str(patient["_id"]), "entries": payload.entries or []}
    result = await db["medical_records"].insert_one(doc)
    created = await db["medical_records"].find_one({"_id": result.inserted_id})
    return _record_from_doc(created)


# PUBLIC_INTERFACE
@router.get(
    "/{record_id}",
    response_model=MedicalRecord,
    summary="Get medical record",
    description="Retrieve a medical record. Patients can access their own; doctors/admins can access any.",
)
async def get_medical_record(
    record_id: str = Path(..., description="Medical record id"),
    user_claims: Dict[str, Any] = Depends(get_current_user_strict),
) -> MedicalRecord:
    """Get a specific medical record with RBAC checks."""
    db = await get_db()
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Medical record not found")

    doc = await db["medical_records"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Medical record not found")

    role = user_claims.get("role")
    if role == "admin" or role == "doctor":
        return _record_from_doc(doc)
    if role == "patient":
        own_patient_id = await _get_patient_id_for_user(db, user_claims["sub"])
        if own_patient_id and doc.get("patient_id") == own_patient_id:
            return _record_from_doc(doc)
    raise HTTPException(status_code=403, detail="Insufficient permissions")


# PUBLIC_INTERFACE
@router.patch(
    "/{record_id}",
    response_model=MedicalRecord,
    summary="Update medical record",
    description="Update a medical record. Admins and doctors only.",
)
async def update_medical_record(
    record_id: str,
    payload: MedicalRecordUpdate,
    _: Dict[str, Any] = Depends(role_required_strict(["admin", "doctor"])),
) -> MedicalRecord:
    """Update entries in a medical record."""
    db = await get_db()
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Medical record not found")

    doc = await db["medical_records"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Medical record not found")

    updates: Dict[str, Any] = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if updates:
        await db["medical_records"].update_one({"_id": oid}, {"$set": updates})
    updated = await db["medical_records"].find_one({"_id": oid})
    return _record_from_doc(updated)


# PUBLIC_INTERFACE
@router.delete(
    "/{record_id}",
    status_code=204,
    summary="Delete medical record",
    description="Delete a medical record. Admin only.",
)
async def delete_medical_record(
    record_id: str,
    _: Dict[str, Any] = Depends(role_required_strict(["admin"])),
) -> None:
    """Delete a medical record (admin only)."""
    db = await get_db()
    try:
        oid = ObjectId(record_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Medical record not found")

    result = await db["medical_records"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Medical record not found")

"""Consultations router with CRUD operations and RBAC."""

from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path

from src.api.db import get_db
from src.api.dependencies import get_current_user, role_required
from src.api.models import Consultation, ConsultationCreate, ConsultationUpdate

router = APIRouter(prefix="/consultations", tags=["Consultations"])


def _consultation_from_doc(doc: Dict[str, Any]) -> Consultation:
    """Map a MongoDB consultation document to Consultation model."""
    return Consultation(
        id=str(doc.get("_id") or doc.get("id")),
        patient_id=doc["patient_id"],
        doctor_id=doc["doctor_id"],
        scheduled_at=doc["scheduled_at"],
        notes=doc.get("notes"),
    )


async def _get_patient_id_for_user(db, user_id: str) -> Optional[str]:
    """Get the patient document id for a given user id (as string)."""
    patient = await db["patients"].find_one({"user_id": user_id})
    return str(patient["_id"]) if patient else None


async def _get_doctor_id_for_user(db, user_id: str) -> Optional[str]:
    """Get the doctor document id for a given user id (as string)."""
    doctor = await db["doctors"].find_one({"user_id": user_id})
    return str(doctor["_id"]) if doctor else None


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[Consultation],
    summary="List consultations",
    description="List consultations for the current user (admin: all; doctor: their consultations; patient: their consultations).",
)
async def list_consultations(user_claims: Dict[str, Any] = Depends(get_current_user)) -> List[Consultation]:
    """Return consultations filtered by user role and ownership."""
    db = await get_db()
    role = user_claims.get("role")
    query: Dict[str, Any] = {}

    if role == "admin":
        query = {}
    elif role == "doctor":
        doctor_id = await _get_doctor_id_for_user(db, user_claims["sub"])
        if not doctor_id:
            return []
        query = {"doctor_id": doctor_id}
    else:  # patient
        patient_id = await _get_patient_id_for_user(db, user_claims["sub"])
        if not patient_id:
            return []
        query = {"patient_id": patient_id}

    cursor = db["consultations"].find(query).sort("scheduled_at", -1)
    return [_consultation_from_doc(doc) async for doc in cursor]


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=Consultation,
    status_code=201,
    summary="Create consultation",
    description="Create a new consultation. Doctors create for their own profile; admins can create any.",
)
async def create_consultation(
    payload: ConsultationCreate,
    user_claims: Dict[str, Any] = Depends(role_required(["admin", "doctor"])),
) -> Consultation:
    """Create a consultation, enforcing that doctors can only create for themselves."""
    db = await get_db()
    role = user_claims.get("role")

    doctor_id = payload.doctor_id
    if role == "doctor":
        inferred_doctor_id = await _get_doctor_id_for_user(db, user_claims["sub"])
        if not inferred_doctor_id:
            raise HTTPException(status_code=400, detail="Doctor profile not found for user")
        doctor_id = inferred_doctor_id

    # Validate patient_id and doctor_id existence
    try:
        poid = ObjectId(payload.patient_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid patient_id")

    patient = await db["patients"].find_one({"_id": poid})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if not doctor_id:
        raise HTTPException(status_code=400, detail="doctor_id is required")

    try:
        doid = ObjectId(doctor_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid doctor_id")

    doctor = await db["doctors"].find_one({"_id": doid})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doc: Dict[str, Any] = {
        "patient_id": str(patient["_id"]),
        "doctor_id": str(doctor["_id"]),
        "scheduled_at": payload.scheduled_at,
        "notes": payload.notes,
    }
    result = await db["consultations"].insert_one(doc)
    created = await db["consultations"].find_one({"_id": result.inserted_id})
    return _consultation_from_doc(created)


# PUBLIC_INTERFACE
@router.get(
    "/{consultation_id}",
    response_model=Consultation,
    summary="Get consultation",
    description="Retrieve a consultation by id. Accessible to admin, the assigned doctor, or the patient.",
)
async def get_consultation(
    consultation_id: str = Path(..., description="Consultation document id"),
    user_claims: Dict[str, Any] = Depends(get_current_user),
) -> Consultation:
    """Get a consultation with RBAC checks."""
    db = await get_db()
    try:
        oid = ObjectId(consultation_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Consultation not found")

    doc = await db["consultations"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Consultation not found")

    role = user_claims.get("role")
    if role == "admin":
        return _consultation_from_doc(doc)
    if role == "doctor":
        doctor_id = await _get_doctor_id_for_user(db, user_claims["sub"])
        if doctor_id and doc.get("doctor_id") == doctor_id:
            return _consultation_from_doc(doc)
    if role == "patient":
        patient_id = await _get_patient_id_for_user(db, user_claims["sub"])
        if patient_id and doc.get("patient_id") == patient_id:
            return _consultation_from_doc(doc)

    raise HTTPException(status_code=403, detail="Insufficient permissions")


# PUBLIC_INTERFACE
@router.patch(
    "/{consultation_id}",
    response_model=Consultation,
    summary="Update consultation",
    description="Update a consultation. Admin or assigned doctor can update.",
)
async def update_consultation(
    consultation_id: str,
    payload: ConsultationUpdate,
    user_claims: Dict[str, Any] = Depends(get_current_user),
) -> Consultation:
    """Update a consultation with RBAC checks."""
    db = await get_db()
    try:
        oid = ObjectId(consultation_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Consultation not found")

    doc = await db["consultations"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Consultation not found")

    role = user_claims.get("role")
    if role != "admin":
        doctor_id = await _get_doctor_id_for_user(db, user_claims["sub"])
        if not doctor_id or doc.get("doctor_id") != doctor_id:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    updates: Dict[str, Any] = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if updates:
        await db["consultations"].update_one({"_id": oid}, {"$set": updates})
    updated = await db["consultations"].find_one({"_id": oid})
    return _consultation_from_doc(updated)


# PUBLIC_INTERFACE
@router.delete(
    "/{consultation_id}",
    status_code=204,
    summary="Delete consultation",
    description="Delete a consultation. Admin only.",
)
async def delete_consultation(
    consultation_id: str,
    _: Dict[str, Any] = Depends(role_required(["admin"])),
) -> None:
    """Delete a consultation (admin only)."""
    db = await get_db()
    try:
        oid = ObjectId(consultation_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Consultation not found")

    result = await db["consultations"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Consultation not found")

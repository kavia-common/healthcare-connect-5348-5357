"""Doctors router with CRUD operations and RBAC."""

from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.api.db import get_db
from src.api.dependencies import get_current_user_strict, role_required_strict
from src.api.models import Doctor, DoctorCreate, DoctorUpdate

router = APIRouter(prefix="/doctors", tags=["Doctors"])


def _doctor_from_doc(doc: Dict[str, Any]) -> Doctor:
    """Map a MongoDB doctor document to Doctor model."""
    return Doctor(
        id=str(doc.get("_id") or doc.get("id")),
        user_id=doc["user_id"],
        specialty=doc.get("specialty"),
        bio=doc.get("bio"),
    )


async def _assert_doctor_owner_or_admin(doc: Dict[str, Any], user_claims: Dict[str, Any]) -> None:
    """Raise 403 if the user is not allowed to act on this doctor doc."""
    role = user_claims.get("role")
    if role == "admin":
        return
    if role == "doctor" and doc.get("user_id") == user_claims.get("sub"):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[Doctor],
    summary="List doctors",
    description="List all doctors. Accessible to authenticated users.",
)
async def list_doctors(_: Dict[str, Any] = Depends(get_current_user_strict)) -> List[Doctor]:
    """Return all doctor profiles."""
    db = await get_db()
    cursor = db["doctors"].find({})
    return [ _doctor_from_doc(doc) async for doc in cursor ]


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=Doctor,
    status_code=201,
    summary="Create doctor",
    description="Create a new doctor profile. Admins can create for any user; doctors can create their own.",
)
async def create_doctor(
    payload: DoctorCreate,
    user_claims: Dict[str, Any] = Depends(get_current_user_strict),
) -> Doctor:
    """Create a doctor profile with RBAC rules."""
    db = await get_db()
    role = user_claims.get("role")

    user_id: Optional[str] = payload.user_id
    if role == "doctor":
        user_id = user_claims["sub"]
    elif role != "admin":
        raise HTTPException(status_code=403, detail="Only admins or doctors can create doctor profiles")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    doc: Dict[str, Any] = {"user_id": user_id, "specialty": payload.specialty, "bio": payload.bio}
    result = await db["doctors"].insert_one(doc)
    created = await db["doctors"].find_one({"_id": result.inserted_id})
    return _doctor_from_doc(created)


# PUBLIC_INTERFACE
@router.get(
    "/{doctor_id}",
    response_model=Doctor,
    summary="Get doctor",
    description="Retrieve a doctor profile by id. Admins/doctors/patients can view.",
)
async def get_doctor(
    doctor_id: str = Path(..., description="Doctor document id"),
    _: Dict[str, Any] = Depends(get_current_user_strict),
) -> Doctor:
    """Get a specific doctor profile."""
    db = await get_db()
    try:
        oid = ObjectId(doctor_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doc = await db["doctors"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return _doctor_from_doc(doc)


# PUBLIC_INTERFACE
@router.patch(
    "/{doctor_id}",
    response_model=Doctor,
    summary="Update doctor",
    description="Update a doctor profile. Admin or the doctor owner can update.",
)
async def update_doctor(
    doctor_id: str,
    payload: DoctorUpdate,
    user_claims: Dict[str, Any] = Depends(get_current_user_strict),
) -> Doctor:
    """Update doctor fields with partial payload."""
    db = await get_db()
    try:
        oid = ObjectId(doctor_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Doctor not found")

    doc = await db["doctors"].find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")

    await _assert_doctor_owner_or_admin(doc, user_claims)

    updates: Dict[str, Any] = {k: v for k, v in payload.dict(exclude_unset=True).items()}
    if updates:
        await db["doctors"].update_one({"_id": oid}, {"$set": updates})
    updated = await db["doctors"].find_one({"_id": oid})
    return _doctor_from_doc(updated)


# PUBLIC_INTERFACE
@router.delete(
    "/{doctor_id}",
    status_code=204,
    summary="Delete doctor",
    description="Delete a doctor profile. Admin only.",
)
async def delete_doctor(
    doctor_id: str,
    _: Dict[str, Any] = Depends(role_required_strict(["admin"])),
) -> None:
    """Delete a doctor profile (admin only)."""
    db = await get_db()
    try:
        oid = ObjectId(doctor_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Doctor not found")

    result = await db["doctors"].delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Doctor not found")

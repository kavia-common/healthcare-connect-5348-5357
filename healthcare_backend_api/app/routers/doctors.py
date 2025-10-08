from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.dependencies import get_current_user, get_db, require_roles
from app.models.doctor import DoctorCreate, DoctorPublic, DoctorUpdate
from app.utils.mappers import to_public_id

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=DoctorPublic,
    summary="Create doctor profile",
    description="Create a doctor profile for the authenticated doctor user.",
)
async def create_doctor(
    payload: DoctorCreate,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(require_roles("doctor"))] = None,
) -> DoctorPublic:
    """Create a doctor profile for the current authenticated doctor."""
    if payload.user_id != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="user_id must match the authenticated user")

    existing = await db["doctors"].find_one({"user_id": payload.user_id})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Doctor profile already exists")

    doc = payload.model_dump()
    doc["_id"] = f"doctor::{payload.user_id}"
    await db["doctors"].insert_one(doc)
    return DoctorPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.get(
    "/me",
    response_model=DoctorPublic,
    summary="Get my doctor profile",
    description="Retrieve the doctor profile associated with the authenticated doctor user.",
)
async def get_my_doctor_profile(
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(require_roles("doctor"))] = None,
) -> DoctorPublic:
    """Get the current doctor's profile."""
    doc = await db["doctors"].find_one({"user_id": current_user["id"]})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor profile not found")
    return DoctorPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[DoctorPublic],
    summary="List doctors",
    description="List doctor profiles filtered by specialty and pagination.",
)
async def list_doctors(
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    specialty: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> List[DoctorPublic]:
    """List doctor profiles with optional specialty filter."""
    query = {"specialty": specialty} if specialty else {}
    cursor = db["doctors"].find(query, skip=skip, limit=limit)
    items = [to_public_id(doc) | {"id": doc["_id"]} async for doc in cursor]
    return [DoctorPublic(**it) for it in items]


# PUBLIC_INTERFACE
@router.get(
    "/{doctor_id}",
    response_model=DoctorPublic,
    summary="Get doctor by id",
    description="Retrieve a doctor profile by identifier.",
)
async def get_doctor_by_id(
    doctor_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> DoctorPublic:
    """Get a doctor profile by ID."""
    doc = await db["doctors"].find_one({"_id": doctor_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return DoctorPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.put(
    "/{doctor_id}",
    response_model=DoctorPublic,
    summary="Update doctor profile",
    description="Update fields on a doctor profile.",
)
async def update_doctor(
    doctor_id: str,
    payload: DoctorUpdate,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> DoctorPublic:
    """Update a doctor profile."""
    doc = await db["doctors"].find_one({"_id": doctor_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if current_user["role"] == "doctor" and doc.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify others' profiles")

    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if update:
        await db["doctors"].update_one({"_id": doctor_id}, {"$set": update})
        doc.update(update)
    return DoctorPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.delete(
    "/{doctor_id}",
    status_code=204,
    summary="Delete doctor profile",
    description="Delete a doctor profile by identifier.",
)
async def delete_doctor(
    doctor_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Delete a doctor profile."""
    doc = await db["doctors"].find_one({"_id": doctor_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")

    if current_user["role"] == "doctor" and doc.get("user_id") != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete others' profiles")

    await db["doctors"].delete_one({"_id": doctor_id})
    return None

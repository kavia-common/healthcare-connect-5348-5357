from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.dependencies import get_current_user, get_db
from app.models.consultation import ConsultationCreate, ConsultationPublic, ConsultationUpdate
from app.utils.mappers import to_public_id

router = APIRouter()


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=ConsultationPublic,
    summary="Create consultation",
    description="Create a new consultation between patient and doctor.",
)
async def create_consultation(
    payload: ConsultationCreate,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> ConsultationPublic:
    """Create a new consultation."""
    # Create record; simple owner checks could be added here
    doc = payload.model_dump()
    doc["_id"] = f"consult::{payload.patient_id}::{payload.doctor_id}::{doc['datetime'].isoformat()}"
    await db["consultations"].insert_one(doc)
    return ConsultationPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=List[ConsultationPublic],
    summary="List consultations",
    description="List consultations optionally filtered by patient_id or doctor_id.",
)
async def list_consultations(
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
    patient_id: str | None = None,
    doctor_id: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
) -> List[ConsultationPublic]:
    """List consultations with optional filters."""
    query = {}
    if patient_id:
        query["patient_id"] = patient_id
    if doctor_id:
        query["doctor_id"] = doctor_id

    cursor = db["consultations"].find(query, skip=skip, limit=limit, sort=[("datetime", -1)])
    items = [to_public_id(doc) | {"id": doc["_id"]} async for doc in cursor]
    return [ConsultationPublic(**it) for it in items]


# PUBLIC_INTERFACE
@router.get(
    "/{consultation_id}",
    response_model=ConsultationPublic,
    summary="Get consultation by id",
    description="Retrieve a consultation by identifier.",
)
async def get_consultation_by_id(
    consultation_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> ConsultationPublic:
    """Get a consultation by ID."""
    doc = await db["consultations"].find_one({"_id": consultation_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")
    return ConsultationPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.put(
    "/{consultation_id}",
    response_model=ConsultationPublic,
    summary="Update consultation",
    description="Update consultation details or status.",
)
async def update_consultation(
    consultation_id: str,
    payload: ConsultationUpdate,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
) -> ConsultationPublic:
    """Update a consultation."""
    doc = await db["consultations"].find_one({"_id": consultation_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    update = {k: v for k, v in payload.model_dump().items() if v is not None}
    if update:
        await db["consultations"].update_one({"_id": consultation_id}, {"$set": update})
        doc.update(update)
    return ConsultationPublic(**(to_public_id(doc) | {"id": doc["_id"]}))


# PUBLIC_INTERFACE
@router.delete(
    "/{consultation_id}",
    status_code=204,
    summary="Delete consultation",
    description="Delete a consultation by identifier.",
)
async def delete_consultation(
    consultation_id: str,
    request: Request,
    db=Depends(get_db),
    current_user: Annotated[dict, Depends(get_current_user)] = None,
):
    """Delete a consultation."""
    doc = await db["consultations"].find_one({"_id": consultation_id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")
    await db["consultations"].delete_one({"_id": consultation_id})
    return None

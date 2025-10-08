from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field


class ConsultationBase(BaseModel):
    patient_id: str = Field(..., description="Patient profile ID")
    doctor_id: str = Field(..., description="Doctor profile ID")
    datetime: datetime = Field(..., description="Consultation date and time")
    notes: Optional[str] = Field(None, description="Consultation notes")
    status: Literal["scheduled", "completed", "canceled"] = Field("scheduled", description="Status of the consultation")


class ConsultationCreate(ConsultationBase):
    pass


class ConsultationUpdate(BaseModel):
    datetime: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[Literal["scheduled", "completed", "canceled"]] = None


class ConsultationPublic(ConsultationBase):
    id: str = Field(..., description="Consultation identifier")

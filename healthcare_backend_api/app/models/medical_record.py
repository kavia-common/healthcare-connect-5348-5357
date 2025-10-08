from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MedicalRecordBase(BaseModel):
    patient_id: str = Field(..., description="Patient profile ID")
    doctor_id: str = Field(..., description="Doctor profile ID")
    diagnosis: Optional[str] = Field(None, description="Diagnosis details")
    treatments: Optional[str] = Field(None, description="Treatments or prescriptions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(BaseModel):
    diagnosis: Optional[str] = None
    treatments: Optional[str] = None


class MedicalRecordPublic(MedicalRecordBase):
    id: str = Field(..., description="Medical record identifier")

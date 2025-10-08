from typing import Optional

from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    user_id: str = Field(..., description="Associated user ID")
    age: Optional[int] = Field(None, ge=0, description="Age of the patient")
    gender: Optional[str] = Field(None, description="Gender of the patient")
    address: Optional[str] = Field(None, description="Address")
    phone: Optional[str] = Field(None, description="Phone number")


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    age: Optional[int] = Field(None, ge=0)
    gender: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class PatientPublic(PatientBase):
    id: str = Field(..., description="Patient profile identifier")

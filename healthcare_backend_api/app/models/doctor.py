from typing import Optional

from pydantic import BaseModel, Field


class DoctorBase(BaseModel):
    user_id: str = Field(..., description="Associated user ID")
    specialty: Optional[str] = Field(None, description="Doctor specialty")
    years_experience: Optional[int] = Field(None, ge=0, description="Years of experience")
    bio: Optional[str] = Field(None, description="Short biography")


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    specialty: Optional[str] = None
    years_experience: Optional[int] = Field(None, ge=0)
    bio: Optional[str] = None


class DoctorPublic(DoctorBase):
    id: str = Field(..., description="Doctor profile identifier")

"""Pydantic models for authentication and healthcare domain entities."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """JWT access token response model."""

    access_token: str = Field(..., description="The signed JWT access token.")
    token_type: str = Field("bearer", description="The token type, typically 'bearer'.")


class UserBase(BaseModel):
    """Shared fields among user models."""

    email: str = Field(..., description="User email address.")
    full_name: Optional[str] = Field(None, description="Full name of the user.")
    role: Literal["patient", "doctor", "admin"] = Field(
        "patient", description="Role of the user in the system."
    )


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., description="Plaintext password (will be hashed).")


class UserLogin(BaseModel):
    """Schema for user login."""

    email: str = Field(..., description="User email address.")
    password: str = Field(..., description="Plaintext password.")


class UserPublic(UserBase):
    """Public representation of a user (safe to return to clients)."""

    id: str = Field(..., description="Unique identifier of the user.")


class Patient(BaseModel):
    """Patient domain model."""

    id: str = Field(..., description="Unique identifier of the patient.")
    user_id: str = Field(..., description="Associated user id.")
    age: Optional[int] = Field(None, description="Patient age.")
    gender: Optional[str] = Field(None, description="Patient gender.")
    address: Optional[str] = Field(None, description="Patient address details.")


class PatientCreate(BaseModel):
    """Schema for creating a patient profile."""

    user_id: Optional[str] = Field(
        None, description="Associated user id (admin only, otherwise inferred from the token)."
    )
    age: Optional[int] = Field(None, description="Patient age.")
    gender: Optional[str] = Field(None, description="Patient gender.")
    address: Optional[str] = Field(None, description="Patient address details.")


class PatientUpdate(BaseModel):
    """Schema for updating a patient profile (partial)."""

    age: Optional[int] = Field(None, description="Patient age.")
    gender: Optional[str] = Field(None, description="Patient gender.")
    address: Optional[str] = Field(None, description="Patient address details.")


class Doctor(BaseModel):
    """Doctor domain model."""

    id: str = Field(..., description="Unique identifier of the doctor.")
    user_id: str = Field(..., description="Associated user id.")
    specialty: Optional[str] = Field(None, description="Medical specialty.")
    bio: Optional[str] = Field(None, description="Short bio of the doctor.")


class DoctorCreate(BaseModel):
    """Schema for creating a doctor profile."""

    user_id: Optional[str] = Field(
        None, description="Associated user id (admin only, otherwise inferred from the token)."
    )
    specialty: Optional[str] = Field(None, description="Medical specialty.")
    bio: Optional[str] = Field(None, description="Short bio of the doctor.")


class DoctorUpdate(BaseModel):
    """Schema for updating a doctor profile (partial)."""

    specialty: Optional[str] = Field(None, description="Medical specialty.")
    bio: Optional[str] = Field(None, description="Short bio of the doctor.")


class Consultation(BaseModel):
    """Consultation domain model."""

    id: str = Field(..., description="Unique identifier of the consultation.")
    patient_id: str = Field(..., description="Patient id for the consultation.")
    doctor_id: str = Field(..., description="Doctor id for the consultation.")
    scheduled_at: datetime = Field(..., description="Scheduled datetime for the consultation.")
    notes: Optional[str] = Field(None, description="Notes for the consultation.")


class ConsultationCreate(BaseModel):
    """Schema for creating a consultation."""

    patient_id: str = Field(..., description="Patient id for the consultation.")
    doctor_id: Optional[str] = Field(
        None, description="Doctor id for the consultation (optional for doctor role; inferred from token)."
    )
    scheduled_at: datetime = Field(..., description="Scheduled datetime for the consultation.")
    notes: Optional[str] = Field(None, description="Notes for the consultation.")


class ConsultationUpdate(BaseModel):
    """Schema for updating a consultation (partial)."""

    scheduled_at: Optional[datetime] = Field(None, description="Scheduled datetime for the consultation.")
    notes: Optional[str] = Field(None, description="Notes for the consultation.")


class MedicalRecord(BaseModel):
    """Medical record domain model."""

    id: str = Field(..., description="Unique identifier of the record.")
    patient_id: str = Field(..., description="Associated patient id.")
    entries: List[str] = Field(default_factory=list, description="List of medical record entries or IDs.")


class MedicalRecordCreate(BaseModel):
    """Schema for creating a medical record."""

    patient_id: str = Field(..., description="Associated patient id.")
    entries: List[str] = Field(default_factory=list, description="List of medical record entries or IDs.")


class MedicalRecordUpdate(BaseModel):
    """Schema for updating a medical record (partial)."""

    entries: Optional[List[str]] = Field(None, description="List of medical record entries or IDs.")

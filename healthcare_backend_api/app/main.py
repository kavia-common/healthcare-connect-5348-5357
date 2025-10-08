from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import lifespan
from app.routers.auth import router as auth_router
from app.routers.patients import router as patients_router
from app.routers.doctors import router as doctors_router
from app.routers.consultations import router as consultations_router
from app.routers.medical_records import router as medical_records_router

# Define OpenAPI tags metadata
openapi_tags = [
    {"name": "auth", "description": "Authentication and user registration endpoints."},
    {"name": "patients", "description": "Patient profile management endpoints."},
    {"name": "doctors", "description": "Doctor profile management endpoints."},
    {"name": "consultations", "description": "Consultation scheduling and management endpoints."},
    {"name": "medical_records", "description": "Medical records CRUD and retrieval endpoints."},
]

# Create FastAPI application with metadata and lifespan for DB connection.
app = FastAPI(
    title="Healthcare Connect Backend API",
    version="0.1.0",
    description="FastAPI backend for Healthcare Connect with MongoDB (Motor) and JWT authentication.",
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

# Configure CORS based on environment variable.
origins = settings.CORS_ORIGINS or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with path prefixes and tags
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(patients_router, prefix="/patients", tags=["patients"])
app.include_router(doctors_router, prefix="/doctors", tags=["doctors"])
app.include_router(consultations_router, prefix="/consultations", tags=["consultations"])
app.include_router(medical_records_router, prefix="/medical_records", tags=["medical_records"])


# PUBLIC_INTERFACE
@app.get("/", summary="API health check", tags=["auth"])
def root():
    """Health check endpoint for the API service.

    Returns:
        dict: A simple status message and available docs path.
    """
    return {"status": "ok", "docs": "/docs"}

import logging
import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import ensure_indexes, close_client
from src.api.routers import auth as auth_router
from src.api.routers import consultations as consultations_router
from src.api.routers import doctors as doctors_router
from src.api.routers import medical_records as medical_records_router
from src.api.routers import patients as patients_router

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

tags_metadata = [
    {"name": "Auth", "description": "Authentication and authorization endpoints."},
    {"name": "Patients", "description": "Patient management endpoints."},
    {"name": "Doctors", "description": "Doctor management endpoints."},
    {"name": "Consultations", "description": "Consultation scheduling and retrieval endpoints."},
    {"name": "Medical Records", "description": "Medical records management endpoints."},
]

app = FastAPI(
    title="Healthcare Connect API",
    description="Backend API for healthcare application: authentication, patients, doctors, consultations, medical records.",
    version="0.1.0",
    openapi_tags=tags_metadata,
)


def _parse_cors_origins(value: str | None) -> List[str] | str:
    """Parse CORS origins from CSV env; return '*' or a list of origins."""
    if not value or value.strip() == "*":
        return "*"
    # Split by comma and trim whitespace
    origins = [o.strip() for o in value.split(",") if o.strip()]
    # Ensure Flutter preview and common local hosts are allowed by default
    defaults = {"https://appetize.io", "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"}
    origins = list(set(origins) | defaults)
    return origins


CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
parsed_origins = _parse_cors_origins(CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if parsed_origins == "*" else parsed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", summary="Health Check", tags=["Auth"])
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"message": "Healthy"}


@app.on_event("startup")
async def on_startup() -> None:
    """Application startup hook: ensure database indexes."""
    try:
        await ensure_indexes()
    except Exception as exc:  # pragma: no cover - startup resilience
        logger.warning("Startup tasks failed: %s", exc)


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Application shutdown hook: close resources."""
    try:
        close_client()
    except Exception as exc:  # pragma: no cover
        logger.warning("Shutdown tasks encountered an issue: %s", exc)


# Include routers
app.include_router(auth_router.router)
app.include_router(patients_router.router)
app.include_router(doctors_router.router)
app.include_router(consultations_router.router)
app.include_router(medical_records_router.router)

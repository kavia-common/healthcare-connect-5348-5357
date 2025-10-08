import logging
import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.api.db import ensure_indexes, close_client, verify_connection
from src.api.routers import auth as auth_router
from src.api.routers import consultations as consultations_router
from src.api.routers import doctors as doctors_router
from src.api.routers import medical_records as medical_records_router
from src.api.routers import patients as patients_router

# Load environment variables from .env
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    return {"message": "Healthy", "status": "ok"}


# PUBLIC_INTERFACE
@app.get("/health/db", summary="Database Health Check", tags=["Auth"])
async def db_health_check():
    """Health check endpoint to verify database connectivity."""
    try:
        is_connected = await verify_connection(max_retries=3, retry_delay=0.5)
        if is_connected:
            return {
                "message": "Database connection healthy",
                "status": "ok",
                "database": os.getenv("MONGO_DB", "myapp")
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="Database connection unavailable"
            )
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=f"Database health check failed: {str(exc)}"
        )


@app.on_event("startup")
async def on_startup() -> None:
    """Application startup hook: verify database connection and ensure indexes."""
    logger.info("=" * 60)
    logger.info("Starting Healthcare Connect API")
    logger.info("=" * 60)
    
    # Log configuration
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:5001/myapp")
    mongo_db = os.getenv("MONGO_DB", "myapp")
    
    # Mask password in logs if present
    display_uri = mongo_uri.split('@')[-1] if '@' in mongo_uri else mongo_uri
    logger.info("MongoDB URI: %s", display_uri)
    logger.info("MongoDB Database: %s", mongo_db)
    logger.info("CORS Origins: %s", CORS_ORIGINS)
    
    try:
        # Verify database connection with retries
        logger.info("Verifying database connection...")
        if await verify_connection(max_retries=5, retry_delay=2.0):
            logger.info("✓ Database connection successful")
            
            # Ensure indexes
            logger.info("Ensuring database indexes...")
            await ensure_indexes()
            logger.info("✓ Startup completed successfully")
        else:
            logger.error("✗ Database connection failed - service will start but may have limited functionality")
            logger.error("Please ensure MongoDB is running on the configured URI")
            
    except Exception as exc:
        logger.error("✗ Startup tasks failed: %s", exc, exc_info=True)
        logger.warning("Service starting with degraded functionality")


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Application shutdown hook: close resources."""
    logger.info("Shutting down Healthcare Connect API...")
    try:
        close_client()
        logger.info("✓ Shutdown completed successfully")
    except Exception as exc:
        logger.warning("Shutdown tasks encountered an issue: %s", exc)


# Include routers
app.include_router(auth_router.router)
app.include_router(patients_router.router)
app.include_router(doctors_router.router)
app.include_router(consultations_router.router)
app.include_router(medical_records_router.router)

logger.info("All routers registered successfully")

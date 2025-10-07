"""Database utilities for MongoDB connection and index management."""

import logging
import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://appuser:dbuser123@localhost:5000/?authSource=admin")
MONGO_DB = os.getenv("MONGO_DB", "myapp")

# Initialize a single Motor client instance for the app lifecycle.
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def _init_client() -> None:
    """Initialize the global MongoDB client and database reference."""
    global _client, _db
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URI)
        _db = _client[MONGO_DB]
        logger.info("MongoDB client initialized for database: %s", MONGO_DB)


# Initialize on import to make sure references exist; real connection is lazy in Motor.
_init_client()


# PUBLIC_INTERFACE
async def get_database() -> AsyncIOMotorDatabase:
    """Return the default AsyncIOMotorDatabase instance for the application."""
    assert _db is not None, "Database not initialized"
    return _db


# PUBLIC_INTERFACE
async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Yield the database for FastAPI dependency injection."""
    yield await get_database()


# PUBLIC_INTERFACE
async def get_collection(name: str):
    """Get a collection from the configured database by name."""
    db = await get_database()
    return db[name]


# PUBLIC_INTERFACE
async def ensure_indexes() -> None:
    """Create or ensure indexes on key collections.

    This function is safe to call at startup; it will no-op if the database is not reachable.
    """
    try:
        db = await get_database()

        # Users: ensure unique email
        await db["users"].create_index("email", unique=True)

        # Patients: user_id index
        await db["patients"].create_index("user_id")

        # Doctors: user_id and specialty
        await db["doctors"].create_index("user_id")
        await db["doctors"].create_index("specialty")

        # Consultations: patient_id, doctor_id, scheduled_at
        await db["consultations"].create_index([("patient_id", 1), ("scheduled_at", -1)])
        await db["consultations"].create_index("doctor_id")

        # Medical records: patient_id
        await db["medical_records"].create_index("patient_id")

        logger.info("Indexes ensured for key collections.")
    except Exception as exc:  # pragma: no cover - safeguard for startup robustness
        logger.warning("Skipping index creation. Database might be unavailable: %s", exc)


# PUBLIC_INTERFACE
def close_client() -> None:
    """Close the MongoDB client, intended to be used on application shutdown."""
    global _client, _db
    try:
        if _client is not None:
            _client.close()
            logger.info("MongoDB client closed.")
        # Reset references
        _client = None
        _db = None
    except Exception as exc:  # pragma: no cover
        logger.warning("Error closing MongoDB client: %s", exc)

"""Database utilities for MongoDB connection and index management."""

import asyncio
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/myapp")
MONGO_DB = os.getenv("MONGO_DB", "myapp")

# Initialize a single Motor client instance for the app lifecycle.
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None
_connection_verified = False


def _init_client() -> None:
    """Initialize the global MongoDB client and database reference."""
    global _client, _db
    if _client is None:
        logger.info("Initializing MongoDB client with URI: %s, Database: %s", MONGO_URI.split('@')[-1] if '@' in MONGO_URI else MONGO_URI, MONGO_DB)
        _client = AsyncIOMotorClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,  # 5 second timeout for initial connection
            connectTimeoutMS=10000,
            retryWrites=True,
        )
        _db = _client[MONGO_DB]
        logger.info("MongoDB client initialized for database: %s", MONGO_DB)


# Initialize on import to make sure references exist; real connection is lazy in Motor.
_init_client()


# PUBLIC_INTERFACE
async def verify_connection(max_retries: int = 5, retry_delay: float = 2.0) -> bool:
    """Verify database connection with retry logic.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Initial delay between retries (exponential backoff)
    
    Returns:
        True if connection successful, False otherwise
    """
    global _connection_verified
    
    if _connection_verified:
        return True
    
    for attempt in range(max_retries):
        try:
            if _client is None:
                _init_client()
            
            # Ping the database to verify connection
            await _client.admin.command('ping')
            logger.info("✓ MongoDB connection verified successfully")
            _connection_verified = True
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
            wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
            if attempt < max_retries - 1:
                logger.warning(
                    "MongoDB connection attempt %d/%d failed: %s. Retrying in %.1f seconds...",
                    attempt + 1, max_retries, str(exc), wait_time
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(
                    "MongoDB connection failed after %d attempts. Error: %s",
                    max_retries, str(exc)
                )
                return False
        except Exception as exc:
            logger.error("Unexpected error during MongoDB connection: %s", str(exc))
            return False
    
    return False


# PUBLIC_INTERFACE
async def get_database() -> AsyncIOMotorDatabase:
    """Return the default AsyncIOMotorDatabase instance for the application."""
    if _db is None:
        raise RuntimeError("Database not initialized. Call _init_client() first.")
    
    # Verify connection on first use
    if not _connection_verified:
        await verify_connection()
    
    return _db


# PUBLIC_INTERFACE
async def get_db() -> AsyncIOMotorDatabase:
    """Return the database for FastAPI dependency injection and direct use."""
    return await get_database()


# PUBLIC_INTERFACE
async def get_collection(name: str):
    """Get a collection from the configured database by name."""
    db = await get_database()
    return db[name]


# PUBLIC_INTERFACE
async def ensure_indexes() -> None:
    """Create or ensure indexes on key collections.

    This function is safe to call at startup; it will retry if the database is not reachable.
    """
    try:
        # First verify the connection
        if not await verify_connection(max_retries=3, retry_delay=1.0):
            logger.error("Cannot ensure indexes: database connection unavailable")
            return
        
        db = await get_database()

        # Users: ensure unique email
        await db["users"].create_index("email", unique=True)
        logger.info("✓ Index created: users.email (unique)")

        # Patients: ensure unique user_id (1-1 user to patient profile)
        await db["patients"].create_index("user_id", unique=True)
        logger.info("✓ Index created: patients.user_id (unique)")

        # Doctors: ensure unique user_id and index specialty
        await db["doctors"].create_index("user_id", unique=True)
        await db["doctors"].create_index("specialty")
        logger.info("✓ Indexes created: doctors.user_id (unique), doctors.specialty")

        # Consultations: patient_id, doctor_id, scheduled_at
        await db["consultations"].create_index([("patient_id", 1), ("scheduled_at", -1)])
        await db["consultations"].create_index("doctor_id")
        logger.info("✓ Indexes created: consultations (patient_id, scheduled_at), consultations.doctor_id")

        # Medical records: patient_id
        await db["medical_records"].create_index("patient_id")
        logger.info("✓ Index created: medical_records.patient_id")

        # Tokens/Sessions: user_id and created_at for efficient lookups and cleanup
        await db["tokens"].create_index("user_id")
        await db["tokens"].create_index("created_at")
        logger.info("✓ Indexes created: tokens.user_id, tokens.created_at")

        # Sessions: user_id and created_at (if using separate sessions collection)
        await db["sessions"].create_index("user_id")
        await db["sessions"].create_index("created_at")
        logger.info("✓ Indexes created: sessions.user_id, sessions.created_at")

        logger.info("✓ All database indexes ensured successfully")
        
    except Exception as exc:
        logger.error("Failed to ensure indexes: %s", exc, exc_info=True)
        raise


# PUBLIC_INTERFACE
def close_client() -> None:
    """Close the MongoDB client, intended to be used on application shutdown."""
    global _client, _db, _connection_verified
    try:
        if _client is not None:
            _client.close()
            logger.info("MongoDB client closed")
        # Reset references
        _client = None
        _db = None
        _connection_verified = False
    except Exception as exc:
        logger.warning("Error closing MongoDB client: %s", exc)
